#!/usr/bin/env python3
"""
后端服务配置文件
包含数据库配置、API 密钥、第三方服务 URL 等
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 项目路径配置 ====================

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 后端目录
BACKEND_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "output"

# 确保目录存在
for dir_path in [DATA_DIR, LOGS_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==================== 数据库配置 ====================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'EcommerceAgent2026!'),
    'database': os.getenv('DB_NAME', 'ecommerce_agent'),
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor'
}

# 数据库连接池配置
DB_POOL_CONFIG = {
    'min_connections': 5,
    'max_connections': 20,
    'connect_timeout': 10,
    'pool_name': 'ecommerce_pool'
}

# ==================== Rainforest API 配置 ====================

RAINFOREST_CONFIG = {
    'api_key': os.getenv('RAINFOREST_API_KEY', '4459EA5ABF49448BAA6829CE5CE1587C'),
    'base_url': 'https://api.rainforestapi.com/request',
    'timeout': 30,
    'supported_domains': [
        'amazon.com',
        'amazon.co.uk',
        'amazon.de',
        'amazon.fr',
        'amazon.co.jp',
        'amazon.ca',
        'amazon.com.au'
    ]
}

# ==================== ScraperAPI 配置 ====================

SCRAPERAPI_CONFIG = {
    'api_key': os.getenv('SCRAPERAPI_API_KEY', 'a03095a3ea309111095c445b10cc9018'),
    'base_url': 'https://api.scraperapi.com',
    'timeout': 60,
    'premium_required': ['temu.com']  # 需要 premium 代理的域名
}

# ==================== 业务配置 ====================

# 利润计算配置
PROFIT_CONFIG = {
    'retail_price_multiplier': float(os.getenv('RETAIL_PRICE_MULTIPLIER', '3.5')),
    'shipping_cost': float(os.getenv('SHIPPING_COST', '5.0')),
    'min_profit_margin': float(os.getenv('MIN_PROFIT_MARGIN', '0.3')),
    'target_profit_margin': float(os.getenv('TARGET_PROFIT_MARGIN', '0.4'))
}

# 采集配置
COLLECTION_CONFIG = {
    'default_limit': 20,
    'max_limit': 100,
    'default_platforms': ['1688', 'amazon'],
    'cache_enabled': True,
    'cache_ttl': 3600  # 缓存有效期（秒）
}

# ==================== 服务配置 ====================

# FastAPI 服务配置
SERVER_CONFIG = {
    'host': os.getenv('SERVER_HOST', '0.0.0.0'),
    'port': int(os.getenv('SERVER_PORT', 8000)),
    'debug': os.getenv('DEBUG', 'false').lower() == 'true',
    'reload': os.getenv('RELOAD', 'false').lower() == 'true'
}

# CORS 配置
CORS_CONFIG = {
    'allow_origins': ['*'],
    'allow_credentials': True,
    'allow_methods': ['*'],
    'allow_headers': ['*']
}

# ==================== 日志配置 ====================

LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': str(LOGS_DIR / 'backend.log'),
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# ==================== 功能开关 ====================

FEATURE_FLAGS = {
    'enable_amazon': True,
    'enable_1688': True,
    'enable_temu': False,  # Temu 采集受限，默认关闭
    'enable_auto_import': True,
    'enable_cache': True,
    'enable_rate_limit': False
}

# ==================== 验证配置 ====================

def validate_config():
    """验证配置是否完整"""
    errors = []
    
    # 验证数据库配置
    if not DB_CONFIG['password']:
        errors.append("数据库密码未配置")
    
    # 验证 API 密钥
    if not RAINFOREST_CONFIG['api_key']:
        errors.append("Rainforest API 密钥未配置")
    
    if errors:
        raise ValueError(f"配置错误：{', '.join(errors)}")
    
    return True

# ==================== 辅助函数 ====================

def get_database_url():
    """获取数据库连接 URL"""
    return (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?charset={DB_CONFIG['charset']}"
    )

def is_feature_enabled(feature_name):
    """检查功能是否启用"""
    return FEATURE_FLAGS.get(feature_name, False)

# ==================== 初始化验证 ====================

if __name__ == '__main__':
    print("配置验证中...")
    try:
        validate_config()
        print("✅ 配置验证通过")
        print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}")
        print(f"Rainforest API: {RAINFOREST_CONFIG['api_key'][:10]}...")
        print(f"ScraperAPI: {SCRAPERAPI_CONFIG['api_key'][:10]}...")
        print(f"服务端口：{SERVER_CONFIG['port']}")
    except ValueError as e:
        print(f"❌ 配置错误：{e}")
