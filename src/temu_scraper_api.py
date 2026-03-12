#!/usr/bin/env python3
"""
Temu 商品采集模块 - 使用第三方 API 服务

支持的 API 服务：
1. Rainforest API - https://www.rainforestapi.com
2. ScraperAPI - https://www.scraperapi.com
3. Oxylabs - https://oxylabs.io
4. Bright Data - https://brightdata.com
"""

import os
import json
import logging
import requests
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class TemuScraper:
    """Temu 商品采集器 - 使用第三方 API"""
    
    def __init__(self, api_service: str = 'rainforest', api_key: str = None):
        """
        Args:
            api_service: API 服务商 (rainforest, scraperapi, oxylabs, brightdata)
            api_key: API 密钥
        """
        self.api_service = api_service
        self.api_key = api_key or os.getenv(f'{api_service.upper()}_API_KEY')
        
        if not self.api_key:
            logger.warning(f"未找到 {api_service} API 密钥，请设置环境变量或传入 api_key 参数")
        
        # API 配置
        self.api_configs = {
            'rainforest': {
                'base_url': 'https://api.rainforestapi.com/request',
                'params': {
                    'api_key': self.api_key,
                    'type': 'search',
                    'amazon_domain': 'temu.com',  # Rainforest 支持 Temu
                }
            },
            'scraperapi': {
                'base_url': 'https://api.scraperapi.com',
                'params': {
                    'api_key': self.api_key,
                    'render': 'true',
                }
            },
            'oxylabs': {
                'base_url': 'https://realtime.oxylabs.io/v1/queries',
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {self.api_key}'
                }
            },
            'brightdata': {
                'base_url': 'https://api.brightdata.com/scraper/temu',
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            }
        }
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索 Temu 商品
        
        Args:
            keyword: 搜索关键词
            limit: 返回商品数量
            
        Returns:
            商品列表
        """
        if not self.api_key:
            logger.error("API 密钥未配置")
            return []
        
        logger.info(f"开始搜索 Temu 商品：{keyword}")
        
        try:
            if self.api_service == 'rainforest':
                return self._search_rainforest(keyword, limit)
            elif self.api_service == 'scraperapi':
                return self._search_scraperapi(keyword, limit)
            elif self.api_service == 'oxylabs':
                return self._search_oxylabs(keyword, limit)
            elif self.api_service == 'brightdata':
                return self._search_brightdata(keyword, limit)
            else:
                logger.error(f"不支持的 API 服务：{self.api_service}")
                return []
                
        except Exception as e:
            logger.error(f"搜索失败：{e}")
            return []
    
    def _search_rainforest(self, keyword: str, limit: int) -> List[Dict]:
        """使用 Rainforest API 搜索"""
        params = self.api_configs['rainforest']['params'].copy()
        params['search_term'] = keyword
        params['sort_by'] = 'featured'
        
        try:
            response = requests.get(
                self.api_configs['rainforest']['base_url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'search_results' not in data:
                logger.warning("未找到搜索结果")
                return []
            
            products = []
            for item in data['search_results'][:limit]:
                product = {
                    'title': item.get('title', ''),
                    'price': item.get('price', {}).get('value'),
                    'currency': item.get('price', {}).get('currency', 'USD'),
                    'rating': item.get('rating'),
                    'ratings_total': item.get('ratings_total'),
                    'image': item.get('image', {}).get('link'),
                    'url': item.get('link'),
                    'position': item.get('position'),
                    'is_prime': item.get('is_prime', False),
                    'platform': 'Temu',
                    'extracted_at': data.get('request_info', {}).get('success_time', '')
                }
                products.append(product)
            
            logger.info(f"成功提取 {len(products)} 个商品")
            return products
            
        except Exception as e:
            logger.error(f"Rainforest API 请求失败：{e}")
            return []
    
    def _search_scraperapi(self, keyword: str, limit: int) -> List[Dict]:
        """使用 ScraperAPI 搜索"""
        search_url = f"https://www.temu.com/search_result.html?search_key={keyword}"
        
        params = self.api_configs['scraperapi']['params'].copy()
        params['url'] = search_url
        
        try:
            response = requests.get(
                self.api_configs['scraperapi']['base_url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            html = response.text
            
            # 解析 HTML 提取商品（需要 BeautifulSoup）
            products = self._parse_temu_html(html, limit)
            logger.info(f"成功提取 {len(products)} 个商品")
            return products
            
        except Exception as e:
            logger.error(f"ScraperAPI 请求失败：{e}")
            return []
    
    def _search_oxylabs(self, keyword: str, limit: int) -> List[Dict]:
        """使用 Oxylabs 搜索"""
        payload = {
            'source': 'temu_search',
            'query': keyword,
            'domain': 'com',
            'limit': limit
        }
        
        try:
            response = requests.post(
                self.api_configs['oxylabs']['base_url'],
                headers=self.api_configs['oxylabs']['headers'],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'results' not in data:
                return []
            
            products = []
            for item in data['results'][:limit]:
                product = {
                    'title': item.get('title'),
                    'price': item.get('price'),
                    'image': item.get('image'),
                    'url': item.get('url'),
                    'platform': 'Temu'
                }
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Oxylabs 请求失败：{e}")
            return []
    
    def _search_brightdata(self, keyword: str, limit: int) -> List[Dict]:
        """使用 Bright Data 搜索"""
        payload = {
            'keyword': keyword,
            'limit': limit,
            'render': True
        }
        
        try:
            response = requests.post(
                self.api_configs['brightdata']['base_url'],
                headers=self.api_configs['brightdata']['headers'],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get('products', [])
            
        except Exception as e:
            logger.error(f"Bright Data 请求失败：{e}")
            return []
    
    def _parse_temu_html(self, html: str, limit: int) -> List[Dict]:
        """解析 Temu HTML（备用方案）"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            products = []
            
            # Temu 商品列表选择器（可能需要调整）
            product_cards = soup.select('.product-card, .search-product-item, [data-testid="product-item"]')
            
            for card in product_cards[:limit]:
                try:
                    title_el = card.select_one('.product-title, .title, h2, h3')
                    price_el = card.select_one('.price, .current-price, .sale-price')
                    image_el = card.select_one('img')
                    link_el = card.select_one('a')
                    
                    product = {
                        'title': title_el.get_text(strip=True) if title_el else '',
                        'price': price_el.get_text(strip=True) if price_el else '',
                        'image': image_el.get('src') if image_el else '',
                        'url': link_el.get('href') if link_el else '',
                        'platform': 'Temu'
                    }
                    
                    if product['title']:
                        products.append(product)
                        
                except Exception as e:
                    logger.debug(f"解析商品失败：{e}")
                    continue
            
            return products
            
        except ImportError:
            logger.error("需要安装 BeautifulSoup: pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"HTML 解析失败：{e}")
            return []
    
    def save_products(self, products: List[Dict], output_file: str = None):
        """保存商品数据"""
        if output_file is None:
            output_file = Path(__file__).parent.parent / 'data' / 'temu_products.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存 {len(products)} 个商品到 {output_file}")


def search_temu_products(
    keyword: str,
    limit: int = 20,
    api_service: str = 'rainforest',
    api_key: str = None
) -> List[Dict]:
    """
    便捷函数：搜索 Temu 商品
    
    Args:
        keyword: 搜索关键词
        limit: 返回商品数量
        api_service: API 服务商
        api_key: API 密钥
        
    Returns:
        商品列表
    """
    scraper = TemuScraper(api_service=api_service, api_key=api_key)
    products = scraper.search_products(keyword, limit)
    
    if products:
        scraper.save_products(products)
    
    return products


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("Temu 商品采集测试")
    print("="*60)
    
    # 从环境变量获取 API 密钥
    api_key = os.getenv('RAINFOREST_API_KEY')
    
    if not api_key:
        print("\n⚠️  未配置 API 密钥")
        print("\n请设置环境变量:")
        print("  export RAINFOREST_API_KEY=your_api_key")
        print("\n或使用其他 API 服务:")
        print("  - ScraperAPI: export SCRAPERAPI_API_KEY=your_key")
        print("  - Oxylabs: export OXYLABS_API_KEY=your_key")
        print("  - Bright Data: export BRIGHTDATA_API_KEY=your_key")
    else:
        products = search_temu_products(
            keyword='home goods',
            limit=10,
            api_service='rainforest',
            api_key=api_key
        )
        
        print(f"\n✅ 采集完成：{len(products)} 个商品")
        if products:
            print("\n前 3 个商品示例:")
            for i, p in enumerate(products[:3], 1):
                print(f"\n{i}. {p.get('title', 'N/A')[:50]}")
                print(f"   价格：{p.get('price', 'N/A')} {p.get('currency', 'USD')}")
                print(f"   评分：{p.get('rating', 'N/A')}")
