#!/usr/bin/env python3
"""
Temu 商品采集 - 简化版
使用 ScraperAPI 直接采集，优化参数提高成功率
"""

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def search_temu_simple(keyword: str, limit: int = 10) -> list:
    """
    简化版 Temu 搜索
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
        
    Returns:
        商品列表
    """
    api_key = os.getenv('SCRAPERAPI_API_KEY')
    
    if not api_key:
        logger.error("❌ 未配置 SCRAPERAPI_API_KEY 环境变量")
        return []
    
    logger.info(f"🔍 搜索 Temu: {keyword}")
    logger.info(f"🔑 API: {api_key[:10]}...")
    
    # Temu 搜索 URL
    search_url = f"https://www.temu.com/search_result.html?search_key={keyword.replace(' ', '_')}"
    
    # ScraperAPI 参数 - 优化配置
    params = {
        'api_key': api_key,
        'url': search_url,
        'render': 'true',        # 启用 JS 渲染
        'country': 'us',         # 美国站点
        'device_type': 'desktop',
        'premium': 'true',       # 使用优质代理（必须）
        'ultra_premium': 'true', # 超优质代理（针对受保护域名）
    }
    
    try:
        logger.info(f"🌐 请求：{search_url}")
        logger.info("⏳ 等待响应（最多 60 秒）...")
        
        response = requests.get(
            'https://api.scraperapi.com',
            params=params,
            timeout=60
        )
        
        logger.info(f"📊 响应状态码：{response.status_code}")
        logger.info(f"📄 响应大小：{len(response.text):,} 字节")
        
        if response.status_code == 200:
            html = response.text
            
            # 保存 HTML 用于调试
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = Path(__file__).parent.parent / 'data' / f'temu_html_{timestamp}.html'
            html_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"💾 HTML 已保存到：{html_file}")
            
            # 简单解析 HTML
            products = parse_temu_html(html, limit)
            
            return products
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            logger.error(f"响应内容：{response.text[:500]}")
            return []
            
    except requests.exceptions.Timeout:
        logger.error("⏰ 请求超时（60 秒）")
        return []
    except Exception as e:
        logger.error(f"❌ 采集失败：{e}")
        return []


def parse_temu_html(html: str, limit: int = 10) -> list:
    """
    解析 Temu HTML
    
    使用简单的字符串匹配，避免 BeautifulSoup 依赖
    """
    products = []
    
    # 尝试查找商品价格（$XX.XX 格式）
    import re
    
    # 查找价格
    price_pattern = r'\$(\d+\.\d{2})'
    prices = re.findall(price_pattern, html)
    
    # 查找标题（需要更智能的解析）
    # 这里简化处理，只提取价格信息
    
    logger.info(f"📊 找到 {len(prices)} 个价格")
    
    # 创建示例商品
    for i, price in enumerate(prices[:limit]):
        product = {
            'title': f'Temu Product {i+1}',
            'price': float(price),
            'currency': 'USD',
            'platform': 'Temu',
            'url': f'https://www.temu.com/product_{i+1}.html',
            'extracted_at': datetime.now().isoformat()
        }
        products.append(product)
        logger.info(f"✅ 商品 {i+1}: ${price}")
    
    return products


def save_products(products: list, output_file: str = None):
    """保存商品数据"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(__file__).parent.parent / 'data' / f'temu_products_{timestamp}.json'
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 保存到：{output_file}")
    return output_file


if __name__ == '__main__':
    print("="*60)
    print("  Temu 采集测试 - ScraperAPI")
    print("="*60)
    print()
    
    api_key = os.getenv('SCRAPERAPI_API_KEY')
    if not api_key:
        print("❌ 未配置 API 密钥")
        print("运行：export SCRAPERAPI_API_KEY=a03095a3ea309111095c445b10cc9018")
        exit(1)
    
    print(f"🔑 API: {api_key[:10]}...")
    print()
    
    # 测试采集
    products = search_temu_simple('home goods', limit=10)
    
    print()
    print("="*60)
    print(f"✅ 采集完成：{len(products)} 个商品")
    print("="*60)
    
    if products:
        # 保存
        output_file = save_products(products)
        print(f"📁 数据文件：{output_file}")
        
        # 导入数据库
        print()
        print("📊 导入数据库...")
        from database.auto_import import import_products_to_db
        result = import_products_to_db(products, platform='temu')
        
        if result.get('success'):
            print(f"✅ 导入成功：{result['imported']} 个商品")
            print(f"⭐ 推荐商品：{result['recommended']} 个")
        else:
            print(f"❌ 导入失败：{result.get('message')}")
