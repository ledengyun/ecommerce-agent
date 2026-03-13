#!/usr/bin/env python3
"""
亚马逊采集服务层
负责亚马逊商品的采集、处理和分析
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import RAINFOREST_CONFIG, is_feature_enabled
from utils import rainforest_client, normalize_product, calculate_profit
from dao import product_dao

logger = logging.getLogger(__name__)


class AmazonService:
    """亚马逊采集服务"""
    
    def __init__(self):
        self.api_client = rainforest_client
        self.product_dao = product_dao
    
    def search_products(
        self,
        keyword: str,
        limit: int = 20,
        domain: str = 'amazon.com'
    ) -> Dict[str, Any]:
        """
        搜索亚马逊商品
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            domain: 亚马逊站点
            
        Returns:
            采集结果
        """
        # 验证功能开关
        if not is_feature_enabled('enable_amazon'):
            return {
                'success': False,
                'message': '亚马逊采集功能未启用',
                'products': []
            }
        
        # 验证参数
        if not keyword or len(keyword.strip()) == 0:
            return {
                'success': False,
                'message': '关键词不能为空',
                'products': []
            }
        
        if limit < 1 or limit > 100:
            return {
                'success': False,
                'message': '采集数量必须在 1-100 之间',
                'products': []
            }
        
        if domain not in RAINFOREST_CONFIG['supported_domains']:
            return {
                'success': False,
                'message': f'不支持的亚马逊站点：{domain}',
                'products': []
            }
        
        try:
            logger.info(f"开始采集亚马逊：{keyword} @ {domain}")
            
            # 调用 API
            api_response = self.api_client.search_products(
                search_term=keyword.strip(),
                amazon_domain=domain,
                limit=limit
            )
            
            # 检查 API 响应
            if not api_response:
                return {
                    'success': False,
                    'message': 'API 请求失败',
                    'products': []
                }
            
            request_info = api_response.get('request_info', {})
            if not request_info.get('success'):
                return {
                    'success': False,
                    'message': f"API 错误：{request_info.get('error')}",
                    'products': [],
                    'credits_remaining': request_info.get('credits_remaining')
                }
            
            # 解析商品数据
            search_results = api_response.get('search_results', [])
            products = self._parse_products(search_results[:limit], domain)
            
            logger.info(f"成功采集 {len(products)} 个亚马逊商品")
            
            return {
                'success': True,
                'message': f'成功采集 {len(products)} 个商品',
                'keyword': keyword,
                'domain': domain,
                'total_products': len(products),
                'products': products,
                'credits_remaining': request_info.get('credits_remaining')
            }
            
        except Exception as e:
            logger.error(f"亚马逊采集失败：{e}", exc_info=True)
            return {
                'success': False,
                'message': f'采集失败：{str(e)}',
                'products': []
            }
    
    def _parse_products(
        self,
        search_results: List[Dict],
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        解析 API 返回的商品数据
        
        Args:
            search_results: API 返回的搜索结果
            domain: 亚马逊站点
            
        Returns:
            标准化商品列表
        """
        products = []
        
        for item in search_results:
            try:
                # 提取价格
                price_info = item.get('price', {})
                price_value = (
                    price_info.get('value')
                    if isinstance(price_info, dict)
                    else price_info
                )
                
                # 提取图片
                image_info = item.get('image', {})
                image_url = (
                    image_info.get('link')
                    if isinstance(image_info, dict)
                    else image_info
                )
                
                # 构建商品对象
                product = {
                    'title': item.get('title', ''),
                    'price': price_value,
                    'currency': price_info.get('currency', 'USD') if isinstance(price_info, dict) else 'USD',
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
                    'amazon_domain': domain,
                    'extracted_at': datetime.now().isoformat(),
                    'asin': item.get('asin')
                }
                
                # 计算利润
                if price_value:
                    profit_data = calculate_profit(price_value)
                    product.update(profit_data)
                
                products.append(product)
                
            except Exception as e:
                logger.debug(f"解析商品失败：{e}")
                continue
        
        return products
    
    def import_products(
        self,
        products: List[Dict[str, Any]],
        auto_analyze: bool = True
    ) -> Dict[str, Any]:
        """
        导入商品到数据库
        
        Args:
            products: 商品列表
            auto_analyze: 是否自动分析
            
        Returns:
            导入结果
        """
        if not products:
            return {
                'success': False,
                'message': '没有商品数据',
                'imported': 0
            }
        
        try:
            logger.info(f"开始导入 {len(products)} 个商品到数据库")
            
            # 批量插入
            imported_count = self.product_dao.insert_products_batch(products)
            
            logger.info(f"成功导入 {imported_count} 个商品")
            
            # 获取统计
            stats = self.product_dao.get_stats()
            
            return {
                'success': True,
                'message': f'成功导入 {imported_count} 个商品',
                'imported': imported_count,
                'total_in_db': stats.get('total_products', 0),
                'recommended': stats.get('recommended_count', 0),
                'avg_profit_margin': float(stats.get('avg_profit_margin', 0)) * 100 if stats.get('avg_profit_margin') else 0
            }
            
        except Exception as e:
            logger.error(f"导入商品失败：{e}", exc_info=True)
            return {
                'success': False,
                'message': f'导入失败：{str(e)}',
                'imported': 0
            }
    
    def get_product_details(self, asin: str, domain: str = 'amazon.com') -> Optional[Dict[str, Any]]:
        """
        获取商品详情
        
        Args:
            asin: 商品 ASIN
            domain: 亚马逊站点
            
        Returns:
            商品详情
        """
        try:
            details = self.api_client.get_product_details(asin, domain)
            
            if details:
                return {
                    'success': True,
                    'product': details
                }
            
            return {
                'success': False,
                'message': '未找到商品',
                'product': None
            }
            
        except Exception as e:
            logger.error(f"获取商品详情失败：{e}")
            return {
                'success': False,
                'message': str(e),
                'product': None
            }
    
    def check_api_status(self) -> Dict[str, Any]:
        """检查 API 状态"""
        try:
            credits = self.api_client.check_credits()
            
            return {
                'status': 'online',
                'api_configured': bool(RAINFOREST_CONFIG['api_key']),
                'api_key_prefix': RAINFOREST_CONFIG['api_key'][:10] if RAINFOREST_CONFIG['api_key'] else None,
                'credits_remaining': credits,
                'supported_domains': RAINFOREST_CONFIG['supported_domains']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# 全局服务实例
amazon_service = AmazonService()


# 便捷函数
def get_amazon_service():
    """获取 AmazonService 实例"""
    return amazon_service
