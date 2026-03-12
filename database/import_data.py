#!/usr/bin/env python3
"""
电商选品 Agent - 数据导入脚本
将 JSON 数据导入 MySQL 数据库
"""

import json
import pymysql
from pathlib import Path
import re

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'EcommerceAgent2026!',
    'database': 'ecommerce_agent',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def parse_price(price_str):
    """解析价格字符串"""
    if not price_str:
        return None
    
    price_str = str(price_str).strip()
    
    # 排除明显不是价格的（如标题中包含¥的）
    if len(price_str) > 20 or '≥' in price_str or '件' in price_str or '条' in price_str:
        # 尝试提取第一个价格
        match = re.search(r'[¥￥]\s*([\d.]+)', price_str)
        if match:
            return float(match.group(1))
        return None
    
    match = re.search(r'[¥￥]?\s*([\d.]+)', price_str)
    if match:
        return float(match.group(1))
    return None

def import_products():
    """导入商品数据"""
    # 读取 JSON 数据
    data_dir = Path(__file__).parent.parent / 'data'
    products_file = data_dir / '1688_products.json'
    
    if not products_file.exists():
        print(f"❌ 文件不存在：{products_file}")
        return
    
    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理嵌套格式（自动保存版）和扁平格式（旧版）
    if isinstance(data, dict) and 'products' in data:
        products = data['products']
    elif isinstance(data, list):
        products = data
    else:
        print(f"❌ 无效的 JSON 格式")
        return
    
    print(f"📦 读取到 {len(products)} 个商品")
    
    # 连接数据库
    conn = pymysql.connect(**{k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'})
    cursor = conn.cursor()
    
    try:
        # 清空现有数据
        cursor.execute("TRUNCATE TABLE products")
        print("🗑️  已清空现有数据")
        
        # 插入新数据
        for p in products:
            supplier_price = parse_price(p.get('supplier_price') or p.get('price'))
            
            # 计算建议零售价和利润率
            if supplier_price:
                suggested_retail = supplier_price * 3.5
                estimated_cost = supplier_price + 5
                profit = suggested_retail - estimated_cost
                profit_margin = profit / suggested_retail if suggested_retail > 0 else 0
                recommend = profit_margin >= 0.3
            else:
                suggested_retail = None
                profit_margin = None
                recommend = False
            
            sql = """
            INSERT INTO products 
            (title, price, supplier_price, retail_price, profit_margin, 
             image_url, source_url, sales, rating, recommend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                p.get('title', '未知商品'),
                p.get('price'),
                supplier_price,
                suggested_retail,
                profit_margin,
                p.get('image') or p.get('image_url'),  # 兼容两种字段名
                p.get('url') or p.get('source_url'),    # 兼容两种字段名
                p.get('sales'),
                p.get('rating'),
                recommend
            )
            
            cursor.execute(sql, values)
        
        conn.commit()
        print(f"✅ 成功导入 {len(products)} 个商品到数据库")
        
        # 显示统计
        cursor.execute("SELECT * FROM v_product_stats")
        stats = cursor.fetchone()
        print(f"\n📊 数据统计:")
        print(f"   总商品数：{stats[0]}")
        print(f"   推荐商品：{stats[1]}")
        if stats[2]:
            print(f"   平均利润率：{float(stats[2]):.2%}")
        else:
            print(f"   平均利润率：N/A")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 导入失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    import_products()
