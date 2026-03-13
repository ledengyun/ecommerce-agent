"""
业务逻辑层模块
"""

from .amazon_service import AmazonService, amazon_service, get_amazon_service

__all__ = [
    'AmazonService',
    'amazon_service',
    'get_amazon_service'
]
