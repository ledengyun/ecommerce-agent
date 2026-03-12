#!/usr/bin/env python3
"""
统一数据采集模块
支持多个电商平台：1688、Temu、Amazon 等
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """数据采集基类"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.products = []
    
    @abstractmethod
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索商品"""
        pass
    
    def save_products(self, products: List[Dict], output_file: str = None):
        """保存商品数据"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(__file__).parent.parent / 'data' / f'{self.platform}_products_{timestamp}.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'platform': self.platform,
            'extracted_at': datetime.now().isoformat(),
            'total_products': len(products),
            'products': products
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存 {len(products)} 个商品到 {output_file}")
        return output_file
    
    def load_products(self, input_file: str) -> List[Dict]:
        """加载商品数据"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('products', [])


class Scraper1688(BaseScraper):
    """1688 数据采集器"""
    
    def __init__(self):
        super().__init__('1688')
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        1688 商品搜索（人工辅助模式）
        
        说明：由于 1688 反爬限制，推荐使用人工辅助方式
        1. 人工访问 1688.com
        2. 搜索关键词
        3. 运行 scripts/extract_1688_auto.js
        4. 自动下载 JSON 文件
        """
        logger.info(f"1688 采集提示：请访问 1688.com 搜索 '{keyword}'")
        logger.info("运行脚本：scripts/extract_1688_auto.js")
        
        # 检查是否有已采集的数据
        data_dir = Path(__file__).parent.parent / 'data'
        files = list(data_dir.glob('1688_products_*.json'))
        
        if files:
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            logger.info(f"找到已采集数据：{latest_file}")
            return self.load_products(str(latest_file))
        
        logger.warning("未找到已采集的 1688 数据")
        return []


class ScraperTemu(BaseScraper):
    """Temu 数据采集器 - 使用第三方 API"""
    
    def __init__(self, api_service: str = 'rainforest', api_key: str = None):
        super().__init__('temu')
        self.api_service = api_service
        self.api_key = api_key or os.getenv(f'{api_service.upper()}_API_KEY')
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Temu 商品搜索"""
        if not self.api_key:
            logger.warning(f"未配置 {self.api_service} API 密钥")
            return []
        
        try:
            # 导入 Temu 采集器
            from src.temu_scraper_api import TemuScraper
            
            scraper = TemuScraper(
                api_service=self.api_service,
                api_key=self.api_key
            )
            
            products = scraper.search_products(keyword, limit)
            
            if products:
                output_file = scraper.save_products(products)
                logger.info(f"Temu 数据采集完成：{output_file}")
            
            return products
            
        except ImportError:
            logger.error("需要安装 temu_scraper_api 模块")
            return []
        except Exception as e:
            logger.error(f"Temu 采集失败：{e}")
            return []


class ScraperAmazon(BaseScraper):
    """Amazon 数据采集器 - 使用第三方 API"""
    
    def __init__(self, api_service: str = 'rainforest', api_key: str = None):
        super().__init__('amazon')
        self.api_service = api_service
        self.api_key = api_key or os.getenv(f'{api_service.upper()}_API_KEY')
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Amazon 商品搜索"""
        if not self.api_key:
            logger.warning(f"未配置 {self.api_service} API 密钥")
            return []
        
        try:
            # 使用 Rainforest API
            import requests
            
            params = {
                'api_key': self.api_key,
                'type': 'search',
                'amazon_domain': 'amazon.com',
                'search_term': keyword,
                'sort_by': 'featured'
            }
            
            response = requests.get(
                'https://api.rainforestapi.com/request',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'search_results' not in data:
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
                    'is_prime': item.get('is_prime', False),
                    'platform': 'Amazon',
                    'extracted_at': datetime.now().isoformat()
                }
                products.append(product)
            
            logger.info(f"Amazon 采集完成：{len(products)} 个商品")
            return products
            
        except Exception as e:
            logger.error(f"Amazon 采集失败：{e}")
            return []


class DataCollector:
    """统一数据采集管理器"""
    
    def __init__(self):
        self.scrapers = {
            '1688': Scraper1688(),
            'temu': ScraperTemu(),
            'amazon': ScraperAmazon()
        }
        self.all_products = []
    
    def collect(
        self,
        keyword: str,
        platforms: List[str] = None,
        limit_per_platform: int = 20,
        output_file: str = None
    ) -> Dict[str, List[Dict]]:
        """
        采集多个平台的商品数据
        
        Args:
            keyword: 搜索关键词
            platforms: 平台列表 ['1688', 'temu', 'amazon']
            limit_per_platform: 每个平台采集数量
            output_file: 输出文件路径
            
        Returns:
            各平台商品数据
        """
        if platforms is None:
            platforms = ['1688', 'temu']
        
        logger.info(f"开始采集：{keyword}")
        logger.info(f"平台：{', '.join(platforms)}")
        
        results = {}
        
        for platform in platforms:
            if platform not in self.scrapers:
                logger.warning(f"不支持的平台：{platform}")
                continue
            
            logger.info(f"\n采集 {platform} 平台...")
            scraper = self.scrapers[platform]
            products = scraper.search_products(keyword, limit_per_platform)
            
            results[platform] = products
            logger.info(f"✅ {platform}: {len(products)} 个商品")
        
        # 合并所有商品
        self.all_products = []
        for platform_products in results.values():
            self.all_products.extend(platform_products)
        
        # 保存合并结果
        if output_file and self.all_products:
            self._save_combined_results(output_file, results)
        
        return results
    
    def _save_combined_results(self, output_file: str, results: Dict):
        """保存合并结果"""
        data = {
            'extracted_at': datetime.now().isoformat(),
            'platforms': list(results.keys()),
            'total_products': sum(len(p) for p in results.values()),
            'by_platform': {
                platform: {
                    'count': len(products),
                    'products': products
                }
                for platform, products in results.items()
            },
            'all_products': self.all_products
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n保存合并结果到：{output_file}")
        logger.info(f"总计：{len(self.all_products)} 个商品")
    
    def compare_prices(self, keyword: str = None) -> Dict:
        """
        对比不同平台的商品价格
        
        Args:
            keyword: 关键词（如果为 None，使用已采集的数据）
            
        Returns:
            价格对比结果
        """
        if not self.all_products and keyword:
            self.collect(keyword)
        
        if not self.all_products:
            return {'error': '没有商品数据'}
        
        # 按平台分组
        by_platform = {}
        for product in self.all_products:
            platform = product.get('platform', 'Unknown')
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(product)
        
        # 计算统计数据
        stats = {}
        for platform, products in by_platform.items():
            prices = [p.get('price') for p in products if p.get('price')]
            if prices:
                stats[platform] = {
                    'count': len(products),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'avg_price': sum(prices) / len(prices)
                }
        
        return {
            'keyword': keyword,
            'total_products': len(self.all_products),
            'platforms': list(by_platform.keys()),
            'by_platform': stats,
            'products': self.all_products
        }


def collect_products(
    keyword: str,
    platforms: List[str] = None,
    limit: int = 20,
    output_file: str = None
) -> Dict[str, List[Dict]]:
    """
    便捷函数：采集商品数据
    
    Args:
        keyword: 搜索关键词
        platforms: 平台列表
        limit: 每个平台采集数量
        output_file: 输出文件
        
    Returns:
        各平台商品数据
    """
    collector = DataCollector()
    return collector.collect(keyword, platforms, limit, output_file)


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("多平台数据采集器")
    print("="*60)
    
    # 测试采集
    keyword = 'home goods'
    
    print(f"\n关键词：{keyword}")
    print("平台：1688, Temu")
    print("")
    
    # 采集数据
    collector = DataCollector()
    results = collector.collect(
        keyword=keyword,
        platforms=['1688', 'temu'],
        limit_per_platform=10,
        output_file='data/combined_products.json'
    )
    
    # 显示结果
    print("\n" + "="*60)
    print("采集结果")
    print("="*60)
    
    for platform, products in results.items():
        print(f"\n{platform}: {len(products)} 个商品")
        if products:
            for i, p in enumerate(products[:3], 1):
                print(f"  {i}. {p.get('title', 'N/A')[:40]}")
                print(f"     价格：{p.get('price', 'N/A')}")
    
    # 价格对比
    print("\n" + "="*60)
    print("价格对比")
    print("="*60)
    
    comparison = collector.compare_prices()
    if 'error' not in comparison:
        for platform, stats in comparison.get('by_platform', {}).items():
            print(f"\n{platform}:")
            print(f"  商品数：{stats['count']}")
            print(f"  最低价：${stats['min_price']:.2f}")
            print(f"  最高价：${stats['max_price']:.2f}")
            print(f"  平均价：${stats['avg_price']:.2f}")
