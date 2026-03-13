#!/usr/bin/env python3
"""
HTTP 请求工具类
提供对第三方 API 的请求封装
"""

import logging
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import RAINFOREST_CONFIG, SCRAPERAPI_CONFIG

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP 客户端"""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self):
        """创建会话（带重试机制）"""
        session = requests.Session()
        
        # 配置重试策略
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """GET 请求"""
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"请求超时：{url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败：{e}")
            return None
    
    def post(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """POST 请求"""
        try:
            response = self.session.post(
                url,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"请求超时：{url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败：{e}")
            return None
    
    def close(self):
        """关闭会话"""
        self.session.close()


class RainforestAPIClient:
    """Rainforest API 客户端"""
    
    def __init__(self):
        self.api_key = RAINFOREST_CONFIG['api_key']
        self.base_url = RAINFOREST_CONFIG['base_url']
        self.timeout = RAINFOREST_CONFIG['timeout']
        self.client = HTTPClient(timeout=self.timeout)
    
    def search_products(
        self,
        search_term: str,
        amazon_domain: str = 'amazon.com',
        limit: int = 20
    ) -> Dict:
        """
        搜索亚马逊商品
        
        Args:
            search_term: 搜索关键词
            amazon_domain: 亚马逊站点
            limit: 返回数量
            
        Returns:
            API 响应数据
        """
        params = {
            'api_key': self.api_key,
            'type': 'search',
            'amazon_domain': amazon_domain,
            'search_term': search_term,
            'sort_by': 'featured'
        }
        
        logger.info(f"请求 Rainforest API: {search_term} @ {amazon_domain}")
        
        result = self.client.get(self.base_url, params=params)
        
        if result:
            request_info = result.get('request_info', {})
            if request_info.get('success'):
                credits = request_info.get('credits_remaining')
                logger.info(f"API 请求成功，剩余余额：{credits}")
            else:
                logger.error(f"API 请求失败：{request_info.get('error')}")
        
        return result
    
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
        
        logger.info(f"获取商品详情：{asin}")
        
        result = self.client.get(self.base_url, params=params)
        
        if result and result.get('request_info', {}).get('success'):
            return result.get('product', {})
        
        return {}
    
    def check_credits(self) -> int:
        """检查 API 余额"""
        # 通过一次小请求获取余额
        result = self.search_products('test', limit=1)
        if result:
            return result.get('request_info', {}).get('credits_remaining', 0)
        return 0


class ScraperAPIClient:
    """ScraperAPI 客户端"""
    
    def __init__(self):
        self.api_key = SCRAPERAPI_CONFIG['api_key']
        self.base_url = SCRAPERAPI_CONFIG['base_url']
        self.timeout = SCRAPERAPI_CONFIG['timeout']
        self.client = HTTPClient(timeout=self.timeout)
    
    def get_html(self, url: str, render: bool = False, premium: bool = False) -> Optional[str]:
        """
        获取网页 HTML
        
        Args:
            url: 目标 URL
            render: 是否启用 JS 渲染
            premium: 是否使用 premium 代理
            
        Returns:
            HTML 内容
        """
        params = {
            'api_key': self.api_key,
            'url': url,
        }
        
        if render:
            params['render'] = 'true'
        if premium:
            params['premium'] = 'true'
        
        logger.info(f"请求 ScraperAPI: {url}")
        
        response = self.client.session.get(
            self.base_url,
            params=params,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"ScraperAPI 请求失败：{response.status_code}")
            return None


# 全局客户端实例
rainforest_client = RainforestAPIClient()
scraper_client = ScraperAPIClient()


# 便捷函数
def get_rainforest_client():
    """获取 Rainforest API 客户端"""
    return rainforest_client


def get_scraper_client():
    """获取 ScraperAPI 客户端"""
    return scraper_client
