#!/usr/bin/env python3
"""
亚马逊商品采集模块
使用 Rainforest API - 完美支持 Amazon

API 密钥：4459EA5ABF49448BAA6829CE5CE1587C
余额：92 次请求
"""

import os
import json
import logging
import requests
from typing import List, Dict
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AmazonScraper:
    """亚马逊商品采集器"""
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: Rainforest API 密钥
        """
        self.api_key = api_key or os.getenv('RAINFOREST_API_KEY')
        self.base_url = 'https://api.rainforestapi.com/request'
        
        if not self.api_key:
            raise ValueError("未找到 Rainforest API 密钥")
    
    def search_products(
        self, 
        keyword: str, 
        limit: int = 20,
        amazon_domain: str = 'amazon.com'
    ) -> List[Dict]:
        """
        搜索亚马逊商品
        
        Args:
            keyword: 搜索关键词
            limit: 返回商品数量
            amazon_domain: 亚马逊站点 (amazon.com, amazon.co.uk, amazon.co.jp 等)
            
        Returns:
            商品列表
        """
        logger.info(f"🔍 搜索 Amazon: {keyword}")
        logger.info(f"🌐 站点：{amazon_domain}")
        
        params = {
            'api_key': self.api_key,
            'type': 'search',
            'amazon_domain': amazon_domain,
            'search_term': keyword,
            'sort_by': 'featured'  # featured, price_low_to_high, price_high_to_low, avg_review
        }
        
        try:
            logger.info("⏳ 请求 Rainforest API...")
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # 检查请求是否成功
            request_info = data.get('request_info', {})
            if not request_info.get('success'):
                logger.error(f"❌ API 请求失败：{request_info.get('error')}")
                return []
            
            # 显示余额
            credits = request_info.get('credits_remaining')
            logger.info(f"✅ 请求成功，剩余余额：{credits} 次")
            
            # 提取搜索结果
            search_results = data.get('search_results', [])
            if not search_results:
                logger.warning("⚠️ 未找到搜索结果")
                return []
            
            # 解析商品数据
            products = []
            for item in search_results[:limit]:
                product = self._parse_product(item)
                if product:
                    products.append(product)
            
            logger.info(f"✅ 成功提取 {len(products)} 个商品")
            return products
            
        except requests.exceptions.Timeout:
            logger.error("⏰ 请求超时")
            return []
        except Exception as e:
            logger.error(f"❌ 采集失败：{e}")
            return []
    
    def _parse_product(self, item: Dict) -> Dict:
        """解析单个商品数据"""
        try:
            # 价格处理
            price_info = item.get('price', {})
            price_value = price_info.get('value') if isinstance(price_info, dict) else price_info
            currency = price_info.get('currency', 'USD') if isinstance(price_info, dict) else 'USD'
            
            # 图片处理
            image_info = item.get('image', {})
            image_url = image_info.get('link') if isinstance(image_info, dict) else image_info
            
            product = {
                'title': item.get('title', ''),
                'price': price_value,
                'currency': currency,
                'rating': item.get('rating'),
                'ratings_total': item.get('ratings_total'),
                'reviews_total': item.get('reviews_total'),
                'image': image_url,
                'url': item.get('link'),
                'position': item.get('position'),
                'is_prime': item.get('is_prime', False),
                'is_amazon_choice': item.get('is_amazon_choice', False),
                'is_best_seller': item.get('is_best_seller', False),
                'platform': 'Amazon',
                'amazon_domain': 'amazon.com',
                'extracted_at': datetime.now().isoformat(),
                'asin': item.get('asin')
            }
            
            return product
            
        except Exception as e:
            logger.debug(f"解析商品失败：{e}")
            return None
    
    def get_product_details(self, asin: str, amazon_domain: str = 'amazon.com') -> Dict:
        """
        获取商品详情
        
        Args:
            asin: 商品 ASIN
            amazon_domain: 亚马逊站点
            
        Returns:
            商品详情
        """
        params = {
            'api_key': self.api_key,
            'type': 'product',
            'amazon_domain': amazon_domain,
            'asin': asin
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get('product', {})
            
        except Exception as e:
            logger.error(f"获取商品详情失败：{e}")
            return {}
    
    def save_products(self, products: List[Dict], output_file: str = None) -> str:
        """保存商品数据到 JSON 文件"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(__file__).parent.parent / 'data' / f'amazon_products_{timestamp}.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 保存到：{output_file}")
        return output_file


def search_amazon(
    keyword: str,
    limit: int = 20,
    domain: str = 'amazon.com',
    api_key: str = None
) -> List[Dict]:
    """
    便捷函数：搜索亚马逊商品
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
        domain: 亚马逊站点
        api_key: API 密钥
        
    Returns:
        商品列表
    """
    scraper = AmazonScraper(api_key=api_key)
    products = scraper.search_products(keyword, limit, domain)
    
    if products:
        output_file = scraper.save_products(products)
        logger.info(f"📁 数据已保存到：{output_file}")
    
    return products


if __name__ == '__main__':
    print("="*60)
    print("  亚马逊商品采集 - Rainforest API")
    print("="*60)
    print()
    
    # 配置 API 密钥
    api_key = os.getenv('RAINFOREST_API_KEY', '4459EA5ABF49448BAA6829CE5CE1587C')
    
    if not api_key:
        print("❌ 未配置 API 密钥")
        print("运行：export RAINFOREST_API_KEY=your_key")
        exit(1)
    
    print(f"🔑 API: {api_key[:10]}...")
    print()
    
    # 测试采集
    keyword = 'home goods'
    print(f"🔍 搜索关键词：{keyword}")
    print(f"🌐 亚马逊站点：amazon.com")
    print()
    
    products = search_amazon(
        keyword=keyword,
        limit=10,
        domain='amazon.com',
        api_key=api_key
    )
    
    print()
    print("="*60)
    print(f"✅ 采集完成：{len(products)} 个商品")
    print("="*60)
    
    if products:
        print("\n前 3 个商品示例:")
        for i, p in enumerate(products[:3], 1):
            print(f"\n{i}. {p.get('title', 'N/A')[:60]}")
            print(f"   价格：${p.get('price', 'N/A')}")
            print(f"   评分：{p.get('rating', 'N/A')} ({p.get('ratings_total', 0)} 条评价)")
            print(f"   Prime: {'✓' if p.get('is_prime') else '✗'}")
            print(f"   链接：{p.get('url', 'N/A')[:60]}")
        
        print("\n💾 数据文件位置:")
        print(f"   data/amazon_products_*.json")
        
        # 询问是否导入数据库
        print("\n📊 是否导入数据库？(y/N)")
        try:
            choice = input("> ").strip().lower()
            if choice == 'y':
                from database.auto_import import import_products_to_db
                
                # 转换价格格式
                for p in products:
                    if p.get('price'):
                        p['supplier_price'] = str(p['price'])
                
                result = import_products_to_db(products, platform='amazon')
                
                if result.get('success'):
                    print(f"\n✅ 导入成功：{result['imported']} 个商品")
                    print(f"⭐ 推荐商品：{result['recommended']} 个")
                else:
                    print(f"\n❌ 导入失败：{result.get('message')}")
        except:
            pass
