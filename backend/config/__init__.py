"""
配置模块
"""

from .settings import (
    # 路径配置
    PROJECT_ROOT,
    BACKEND_ROOT,
    DATA_DIR,
    LOGS_DIR,
    OUTPUT_DIR,
    
    # 数据库配置
    DB_CONFIG,
    DB_POOL_CONFIG,
    
    # API 配置
    RAINFOREST_CONFIG,
    SCRAPERAPI_CONFIG,
    
    # 业务配置
    PROFIT_CONFIG,
    COLLECTION_CONFIG,
    
    # 服务配置
    SERVER_CONFIG,
    CORS_CONFIG,
    
    # 日志配置
    LOGGING_CONFIG,
    
    # 功能开关
    FEATURE_FLAGS,
    
    # 辅助函数
    validate_config,
    get_database_url,
    is_feature_enabled
)

__all__ = [
    # 路径
    'PROJECT_ROOT',
    'BACKEND_ROOT',
    'DATA_DIR',
    'LOGS_DIR',
    'OUTPUT_DIR',
    
    # 数据库
    'DB_CONFIG',
    'DB_POOL_CONFIG',
    
    # API
    'RAINFOREST_CONFIG',
    'SCRAPERAPI_CONFIG',
    
    # 业务
    'PROFIT_CONFIG',
    'COLLECTION_CONFIG',
    
    # 服务
    'SERVER_CONFIG',
    'CORS_CONFIG',
    
    # 日志
    'LOGGING_CONFIG',
    
    # 功能
    'FEATURE_FLAGS',
    
    # 函数
    'validate_config',
    'get_database_url',
    'is_feature_enabled'
]
