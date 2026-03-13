"""
API 接口模块
"""

from .amazon_api import router as amazon_router
from .collection_api import router as collection_router

__all__ = ['amazon_router', 'collection_router']
