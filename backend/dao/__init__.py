"""
数据访问层模块
"""

from .product_dao import ProductDAO, product_dao, get_product_dao

__all__ = [
    'ProductDAO',
    'product_dao',
    'get_product_dao'
]
