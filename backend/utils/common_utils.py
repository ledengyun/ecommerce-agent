#!/usr/bin/env python3
"""
通用工具类
提供数据转换、计算、验证等功能
"""

import re
import json
import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP

from config import PROFIT_CONFIG

logger = logging.getLogger(__name__)


def parse_price(price_str: str) -> Optional[float]:
    """
    解析价格字符串
    
    Args:
        price_str: 价格字符串（如 "$12.99", "¥12.78"）
        
    Returns:
        浮点数价格
    """
    if not price_str:
        return None
    
    price_str = str(price_str).strip()
    
    # 尝试提取数字
    match = re.search(r'[\d.]+', price_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    
    return None


def calculate_profit(supplier_price: float) -> Dict[str, Any]:
    """
    计算利润相关数据
    
    Args:
        supplier_price: 供货价
        
    Returns:
        包含零售价、利润率、是否推荐的字典
    """
    if not supplier_price or supplier_price <= 0:
        return {
            'retail_price': None,
            'profit_margin': None,
            'recommend': False
        }
    
    # 从配置获取参数
    multiplier = PROFIT_CONFIG['retail_price_multiplier']
    shipping_cost = PROFIT_CONFIG['shipping_cost']
    min_margin = PROFIT_CONFIG['min_profit_margin']
    
    # 计算
    retail_price = supplier_price * multiplier
    estimated_cost = supplier_price + shipping_cost
    profit = retail_price - estimated_cost
    profit_margin = profit / retail_price if retail_price > 0 else 0
    recommend = profit_margin >= min_margin
    
    return {
        'retail_price': round(retail_price, 2),
        'profit_margin': round(profit_margin, 4),
        'recommend': recommend
    }


def normalize_product(raw_product: Dict, platform: str = 'unknown') -> Dict:
    """
    标准化商品数据格式
    
    Args:
        raw_product: 原始商品数据
        platform: 平台标识
        
    Returns:
        标准化的商品数据
    """
    # 提取标题
    title = (
        raw_product.get('title') or
        raw_product.get('name') or
        raw_product.get('product_title') or
        '未知商品'
    )
    
    # 提取价格
    price_raw = (
        raw_product.get('price') or
        raw_product.get('supplier_price') or
        raw_product.get('sale_price') or
        raw_product.get('current_price')
    )
    
    supplier_price = parse_price(price_raw) if price_raw else None
    
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
        'image_url': (
            raw_product.get('image') or
            raw_product.get('image_url') or
            raw_product.get('main_image') or
            raw_product.get('thumbnail')
        ),
        'source_url': (
            raw_product.get('url') or
            raw_product.get('source_url') or
            raw_product.get('product_url') or
            raw_product.get('link')
        ),
        'sales': raw_product.get('sales') or raw_product.get('sold_count') or '',
        'rating': raw_product.get('rating') or raw_product.get('score'),
        'recommend': profit_data['recommend'],
        'platform': platform,
        'external_id': raw_product.get('id') or raw_product.get('product_id') or raw_product.get('asin')
    }
    
    return normalized


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
        currency: 货币符号
        
    Returns:
        格式化后的字符串
    """
    symbols = {
        'USD': '$',
        'CNY': '¥',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """验证 URL 格式"""
    pattern = r'^https?://[^\s]+$'
    return bool(re.match(pattern, url))


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """截断文本"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_json_loads(json_str: str) -> Optional[Dict]:
    """安全解析 JSON"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """安全序列化 JSON"""
    try:
        return json.dumps(obj, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError):
        return '{}'


def batch_split(items: List, batch_size: int) -> List[List]:
    """
    分批列表
    
    Args:
        items: 原列表
        batch_size: 每批大小
        
    Returns:
        分批后的列表
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def retry_async(func, max_retries: int = 3, delay: float = 1.0):
    """
    重试装饰器（简化版）
    
    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        delay: 重试间隔
    """
    def wrapper(*args, **kwargs):
        last_error = None
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"重试 {i+1}/{max_retries}: {e}")
                if i < max_retries - 1:
                    import time
                    time.sleep(delay)
        
        if last_error:
            raise last_error
    
    return wrapper


# 数据验证器
class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_product(product: Dict) -> bool:
        """验证商品数据"""
        if not product:
            return False
        
        # 必须字段
        required_fields = ['title']
        for field in required_fields:
            if not product.get(field):
                return False
        
        # 价格验证
        if 'price' in product and product['price']:
            price = parse_price(product['price'])
            if price is None or price <= 0:
                return False
        
        return True
    
    @staticmethod
    def validate_collection_request(keyword: str, limit: int) -> bool:
        """验证采集请求"""
        if not keyword or len(keyword.strip()) == 0:
            return False
        
        if limit < 1 or limit > 100:
            return False
        
        return True
