#!/usr/bin/env python3
"""
自动数据导入模块
支持监听目录、HTTP API、直接调用三种方式
将第三方采集的 JSON 数据自动写入 products 表
"""

import os
import sys
import json
import time
import logging
import threading
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import re
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('auto_import')


class DecimalEncoder(json.JSONEncoder):
    """JSON 编码器，支持 Decimal 类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'EcommerceAgent2026!'),
    'database': os.getenv('DB_NAME', 'ecommerce_agent'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 配置
CONFIG = {
    'watch_dir': Path(__file__).parent.parent / 'data' / 'incoming',  # 监听目录
    'processed_dir': Path(__file__).parent.parent / 'data' / 'processed',  # 已处理目录
    'poll_interval': 5,  # 轮询间隔（秒）
    'min_profit_margin': 0.3,  # 最低利润率阈值
    'retail_price_multiplier': 3.5,  # 零售价倍率
    'shipping_cost': 5.0,  # 运费估算
}


def parse_price(price_str) -> Optional[float]:
    """解析价格字符串，提取数值"""
    if not price_str:
        return None
    
    price_str = str(price_str).strip()
    
    # 排除明显不是价格的
    if len(price_str) > 30 or '≥' in price_str or '件' in price_str or '条' in price_str or '顶' in price_str:
        # 尝试提取第一个价格
        match = re.search(r'[¥￥]\s*([\d.]+)', price_str)
        if match:
            return float(match.group(1))
        return None
    
    match = re.search(r'[¥￥]?\s*([\d.]+)', price_str)
    if match:
        return float(match.group(1))
    return None


def calculate_profit(supplier_price: float) -> Dict:
    """计算利润相关数据"""
    suggested_retail = supplier_price * CONFIG['retail_price_multiplier']
    estimated_cost = supplier_price + CONFIG['shipping_cost']
    profit = suggested_retail - estimated_cost
    profit_margin = profit / suggested_retail if suggested_retail > 0 else 0
    recommend = profit_margin >= CONFIG['min_profit_margin']
    
    return {
        'retail_price': float(round(suggested_retail, 2)),
        'profit_margin': float(round(profit_margin, 4)),
        'recommend': recommend
    }


def normalize_product(raw_product: Dict, platform: str = 'unknown') -> Dict:
    """标准化商品数据格式"""
    # 提取关键字段（兼容多种字段名）
    title = (raw_product.get('title') or 
             raw_product.get('name') or 
             raw_product.get('product_title') or 
             '未知商品')
    
    price_raw = (raw_product.get('price') or 
                 raw_product.get('supplier_price') or 
                 raw_product.get('sale_price') or 
                 raw_product.get('current_price'))
    
    supplier_price = parse_price(price_raw)
    
    # 计算利润
    profit_data = calculate_profit(supplier_price) if supplier_price else {
        'retail_price': None,
        'profit_margin': None,
        'recommend': False
    }
    
    # 标准化字段
    normalized = {
        'title': str(title).strip()[:500],
        'price': str(price_raw).strip()[:50] if price_raw else None,
        'supplier_price': supplier_price,
        'retail_price': profit_data['retail_price'],
        'profit_margin': profit_data['profit_margin'],
        'image_url': (raw_product.get('image') or 
                      raw_product.get('image_url') or 
                      raw_product.get('main_image') or 
                      raw_product.get('thumbnail')),
        'source_url': (raw_product.get('url') or 
                       raw_product.get('source_url') or 
                       raw_product.get('product_url') or 
                       raw_product.get('link')),
        'sales': raw_product.get('sales') or raw_product.get('sold_count') or '',
        'rating': raw_product.get('rating') or raw_product.get('score'),
        'recommend': profit_data['recommend'],
        'platform': platform,
        'external_id': raw_product.get('id') or raw_product.get('product_id')
    }
    
    return normalized


def import_products_to_db(products: List[Dict], platform: str = 'unknown', 
                          truncate: bool = False, batch_size: int = 100) -> Dict:
    """
    将商品数据导入数据库
    
    Args:
        products: 商品列表
        platform: 平台标识
        truncate: 是否清空现有数据
        batch_size: 批量插入大小
        
    Returns:
        导入结果统计
    """
    if not products:
        return {'success': False, 'message': '没有商品数据'}
    
    conn = None
    cursor = None
    
    try:
        conn = pymysql.connect(**{k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'})
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        errors = 0
        
        if truncate:
            cursor.execute("TRUNCATE TABLE products")
            logger.info("已清空 products 表")
        
        # 批量插入
        batch = []
        sql = """
        INSERT INTO products 
        (title, price, supplier_price, retail_price, profit_margin, 
         image_url, source_url, sales, rating, recommend)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for i, raw_product in enumerate(products):
            try:
                normalized = normalize_product(raw_product, platform)
                
                values = (
                    normalized['title'],
                    normalized['price'],
                    normalized['supplier_price'],
                    normalized['retail_price'],
                    normalized['profit_margin'],
                    normalized['image_url'],
                    normalized['source_url'],
                    normalized['sales'],
                    normalized['rating'],
                    normalized['recommend']
                )
                
                batch.append(values)
                
                if len(batch) >= batch_size:
                    cursor.executemany(sql, batch)
                    imported += len(batch)
                    batch = []
                    
            except Exception as e:
                errors += 1
                logger.warning(f"处理商品 {i+1} 失败：{e}")
        
        # 插入剩余数据
        if batch:
            cursor.executemany(sql, batch)
            imported += len(batch)
        
        conn.commit()
        
        # 获取统计
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN recommend THEN 1 ELSE 0 END) as recommended FROM products")
        stats = cursor.fetchone()
        
        # 兼容 DictCursor 和普通 Cursor
        total_in_db = stats.get('total') if isinstance(stats, dict) else stats[0]
        recommended = stats.get('recommended') if isinstance(stats, dict) else (stats[1] or 0)
        
        result = {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'total_in_db': total_in_db,
            'recommended': recommended or 0,
            'platform': platform,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 导入完成：{imported} 个商品，推荐：{result['recommended']}")
        return result
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 导入失败：{e}")
        return {'success': False, 'message': str(e), 'errors': errors}
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def process_file(file_path: Path) -> Dict:
    """处理单个 JSON 文件"""
    logger.info(f"📄 处理文件：{file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同格式
        if isinstance(data, dict):
            products = data.get('products', [])
            platform = data.get('platform', 'unknown')
            if not platform and 'page_url' in data:
                if '1688' in data.get('page_url', ''):
                    platform = '1688'
                elif 'temu' in data.get('page_url', ''):
                    platform = 'temu'
                elif 'amazon' in data.get('page_url', ''):
                    platform = 'amazon'
        elif isinstance(data, list):
            products = data
            platform = 'unknown'
        else:
            return {'success': False, 'message': '无效的 JSON 格式'}
        
        logger.info(f"📦 读取到 {len(products)} 个商品，平台：{platform}")
        
        # 导入数据库
        result = import_products_to_db(products, platform, truncate=False)
        
        # 移动文件到已处理目录
        if result.get('success'):
            CONFIG['processed_dir'].mkdir(parents=True, exist_ok=True)
            dest = CONFIG['processed_dir'] / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
            file_path.rename(dest)
            logger.info(f"📁 文件已移动到：{dest}")
            result['processed_file'] = str(dest)
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败：{e}")
        return {'success': False, 'message': f'JSON 解析失败：{e}'}
    except Exception as e:
        logger.error(f"❌ 处理失败：{e}")
        return {'success': False, 'message': str(e)}


def watch_directory():
    """监听目录，自动处理新文件"""
    logger.info(f"👁️ 开始监听目录：{CONFIG['watch_dir']}")
    
    CONFIG['watch_dir'].mkdir(parents=True, exist_ok=True)
    CONFIG['processed_dir'].mkdir(parents=True, exist_ok=True)
    
    processed_files = set()
    
    while True:
        try:
            # 扫描 JSON 文件
            json_files = list(CONFIG['watch_dir'].glob('*.json'))
            
            for file_path in json_files:
                if str(file_path) not in processed_files:
                    logger.info(f"🔔 发现新文件：{file_path.name}")
                    result = process_file(file_path)
                    
                    if result.get('success'):
                        processed_files.add(str(file_path))
                        logger.info(f"✅ 处理成功：{file_path.name}")
                    else:
                        logger.warning(f"⚠️ 处理失败：{file_path.name} - {result.get('message')}")
            
            time.sleep(CONFIG['poll_interval'])
            
        except KeyboardInterrupt:
            logger.info("👋 停止监听")
            break
        except Exception as e:
            logger.error(f"❌ 监听错误：{e}")
            time.sleep(CONFIG['poll_interval'])


# HTTP API 支持（可选）
def start_http_server(port: int = 8080):
    """启动 HTTP 服务器接收数据"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class ImportHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode('utf-8'))
                products = data.get('products', data if isinstance(data, list) else [])
                platform = data.get('platform', 'api')
                
                result = import_products_to_db(products, platform)
                
                self.send_response(200 if result.get('success') else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode())
        
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {'status': 'running', 'watch_dir': str(CONFIG['watch_dir'])}
            self.wfile.write(json.dumps(status).encode())
        
        def log_message(self, format, *args):
            logger.info(f"HTTP: {args[0]}")
    
    server = HTTPServer(('0.0.0.0', port), ImportHandler)
    logger.info(f"🌐 HTTP 服务器启动在端口 {port}")
    server.serve_forever()


def main():
    """主函数 - 支持多种运行模式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动数据导入工具')
    parser.add_argument('--mode', choices=['watch', 'http', 'once'], default='watch',
                       help='运行模式：watch(监听目录), http(API 服务), once(单次导入)')
    parser.add_argument('--file', type=str, help='单次导入的文件路径')
    parser.add_argument('--port', type=int, default=8080, help='HTTP 服务端口')
    parser.add_argument('--truncate', action='store_true', help='导入前清空表')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        if not args.file:
            print("❌ 单次导入模式需要指定 --file 参数")
            sys.exit(1)
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ 文件不存在：{file_path}")
            sys.exit(1)
        
        result = process_file(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2, cls=DecimalEncoder))
        sys.exit(0 if result.get('success') else 1)
    
    elif args.mode == 'http':
        start_http_server(args.port)
    
    else:  # watch mode
        # 设置信号处理
        def signal_handler(sig, frame):
            logger.info("👋 收到停止信号")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        watch_directory()


if __name__ == '__main__':
    main()
