#!/usr/bin/env python3
"""
Temu 商品采集模块 - 使用 ScraperAPI 直接爬取 Temu 网站

ScraperAPI 支持任意网站，包括 Temu
注册地址：https://www.scraperapi.com
免费试用：5000 次 API 调用
"""

import os
import json
import logging
import requests
from typing import Optional, List, Dict
from pathlib import Path
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class TemuDirectScraper:
    """Temu 直接采集器 - 使用 ScraperAPI"""
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: ScraperAPI 密钥
        """
        self.api_key = api_key or os.getenv('SCRAPERAPI_API_KEY')
        self.base_url = 'https://api.scraperapi.com'
        
        if not self.api_key:
            logger.warning("未找到 ScraperAPI 密钥，请设置 SCRAPERAPI_API_KEY 环境变量")
    
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
            logger.error("ScraperAPI 密钥未配置")
            return []
        
        logger.info(f"开始搜索 Temu 商品：{keyword}")
        
        # 构建 Temu 搜索 URL
        search_url = f"https://www.temu.com/search_result.html?search_key={keyword.replace(' ', '_')}"
        
        # ScraperAPI 参数
        params = {
            'api_key': self.api_key,
            'url': search_url,
            'render': 'true',  # 启用 JavaScript 渲染
            'country': 'us',   # 美国站点
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=60  # 需要更长时间等待渲染
            )
            response.raise_for_status()
            html = response.text
            
            # 解析 HTML
            products = self._parse_html(html, limit)
            
            logger.info(f"成功提取 {len(products)} 个商品")
            return products
            
        except requests.exceptions.Timeout:
            logger.error("请求超时，Temu 页面加载较慢")
            return []
        except Exception as e:
            logger.error(f"采集失败：{e}")
            return []
    
    def _parse_html(self, html: str, limit: int) -> List[Dict]:
        """解析 Temu HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            products = []
            
            # Temu 商品卡片选择器（根据实际页面结构调整）
            # 这些选择器可能需要定期更新
            selectors = [
                '[data-testid="product-item"]',
                '.product-card',
                '.search-product-item',
                '.goods-item',
                '[class*="product"]',
                '[class*="goods"]'
            ]
            
            product_cards = []
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    product_cards = cards
                    logger.info(f"使用选择器：{selector} 找到 {len(cards)} 个商品")
                    break
            
            if not product_cards:
                # 备用方案：查找所有包含价格和标题的元素
                logger.info("未找到标准商品卡片，尝试智能匹配...")
                product_cards = self._smart_find_products(soup)
            
            for card in product_cards[:limit]:
                try:
                    product = self._extract_product(card)
                    if product and product.get('title'):
                        products.append(product)
                except Exception as e:
                    logger.debug(f"解析单个商品失败：{e}")
                    continue
            
            return products
            
        except ImportError:
            logger.error("需要安装 BeautifulSoup: pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"HTML 解析失败：{e}")
            return []
    
    def _smart_find_products(self, soup: BeautifulSoup) -> List:
        """智能查找商品元素"""
        candidates = []
        
        # 查找所有可能包含商品信息的 div
        for div in soup.find_all(['div', 'article', 'section']):
            text = div.get_text()
            
            # 检查是否包含价格符号和商品特征
            has_price = '$' in text or '¥' in text
            has_title = len(text) > 20 and len(text) < 200
            not_navigation = not div.find_parent(['nav', 'footer', 'header'])
            
            if has_price and has_title and not_navigation:
                candidates.append(div)
        
        # 去重（移除嵌套的元素）
        unique = []
        for candidate in candidates:
            is_child = False
            for existing in unique:
                if existing in candidate.parents or existing == candidate:
                    is_child = True
                    break
            if not is_child:
                unique.append(candidate)
        
        return unique[:30]  # 最多返回 30 个候选
    
    def _extract_product(self, element) -> Dict:
        """从元素中提取商品信息"""
        product = {
            'platform': 'Temu',
            'extracted_at': ''
        }
        
        # 提取标题
        title_selectors = [
            '[class*="title"]',
            '[class*="name"]',
            'h1', 'h2', 'h3', 'h4',
            '.product-title',
            '[data-testid="product-title"]'
        ]
        
        for selector in title_selectors:
            title_el = element.select_one(selector)
            if title_el and title_el.get_text(strip=True):
                product['title'] = title_el.get_text(strip=True)
                break
        
        if not product.get('title'):
            # 尝试直接获取文本
            text = element.get_text(separator=' ', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                product['title'] = lines[0][:200]  # 限制长度
        
        # 提取价格
        price_selectors = [
            '[class*="price"]',
            '.current-price',
            '.sale-price',
            '[data-testid="product-price"]',
            '.money'
        ]
        
        for selector in price_selectors:
            price_el = element.select_one(selector)
            if price_el:
                price_text = price_el.get_text(strip=True)
                # 提取美元价格
                price_match = re.search(r'\$([\d.]+)', price_text)
                if price_match:
                    product['price'] = float(price_match.group(1))
                    product['currency'] = 'USD'
                break
        
        # 提取图片
        img = element.select_one('img')
        if img:
            product['image'] = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        
        # 提取链接
        link = element.select_one('a')
        if link:
            href = link.get('href', '')
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.temu.com' + href
            product['url'] = href
        
        # 提取评分
        rating_selectors = [
            '[class*="rating"]',
            '[class*="star"]',
            '.rating-score'
        ]
        
        for selector in rating_selectors:
            rating_el = element.select_one(selector)
            if rating_el:
                rating_text = rating_el.get_text(strip=True)
                rating_match = re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    product['rating'] = float(rating_match.group(1))
                break
        
        # 提取销量
        sales_el = element.select_one('[class*="sold"], [class*="sales"]')
        if sales_el:
            product['sales'] = sales_el.get_text(strip=True)
        
        return product
    
    def save_products(self, products: List[Dict], output_file: str = None):
        """保存商品数据"""
        if output_file is None:
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(__file__).parent.parent / 'data' / f'temu_products_{timestamp}.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存 {len(products)} 个商品到 {output_file}")
        return output_file


def search_temu_direct(
    keyword: str,
    limit: int = 20,
    api_key: str = None
) -> List[Dict]:
    """
    便捷函数：直接搜索 Temu 商品
    
    Args:
        keyword: 搜索关键词
        limit: 返回商品数量
        api_key: ScraperAPI 密钥
        
    Returns:
        商品列表
    """
    scraper = TemuDirectScraper(api_key=api_key)
    products = scraper.search_products(keyword, limit)
    
    if products:
        output_file = scraper.save_products(products)
        logger.info(f"数据已保存到：{output_file}")
    
    return products


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("Temu 直接采集测试 (使用 ScraperAPI)")
    print("="*60)
    
    # 检查 API 密钥
    api_key = os.getenv('SCRAPERAPI_API_KEY')
    
    if not api_key:
        print("\n⚠️  未配置 ScraperAPI 密钥")
        print("\n请注册获取免费密钥：")
        print("  https://www.scraperapi.com")
        print("\n然后设置环境变量:")
        print("  export SCRAPERAPI_API_KEY=your_api_key")
        print("\n免费试用：5000 次 API 调用")
    else:
        print(f"\n🔑 使用 API 密钥：{api_key[:10]}...")
        
        products = search_temu_direct(
            keyword='home goods',
            limit=10,
            api_key=api_key
        )
        
        print(f"\n✅ 采集完成：{len(products)} 个商品")
        
        if products:
            print("\n前 3 个商品示例:")
            for i, p in enumerate(products[:3], 1):
                print(f"\n{i}. {p.get('title', 'N/A')[:60]}")
                print(f"   价格：${p.get('price', 'N/A')}")
                print(f"   评分：{p.get('rating', 'N/A')}")
                print(f"   链接：{p.get('url', 'N/A')[:60]}")
