"""
工具模块
"""

from .db_utils import (
    DatabaseManager,
    db_manager,
    get_db,
    execute_sql,
    query_one,
    query_all
)

from .http_utils import (
    HTTPClient,
    RainforestAPIClient,
    ScraperAPIClient,
    rainforest_client,
    scraper_client,
    get_rainforest_client,
    get_scraper_client
)

from .common_utils import (
    parse_price,
    calculate_profit,
    normalize_product,
    format_currency,
    truncate_text,
    batch_split,
    safe_json_loads,
    safe_json_dumps,
    DataValidator
)

__all__ = [
    # 数据库
    'DatabaseManager',
    'db_manager',
    'get_db',
    'execute_sql',
    'query_one',
    'query_all',
    
    # HTTP
    'HTTPClient',
    'RainforestAPIClient',
    'ScraperAPIClient',
    'rainforest_client',
    'scraper_client',
    'get_rainforest_client',
    'get_scraper_client',
    
    # 通用
    'parse_price',
    'calculate_profit',
    'normalize_product',
    'format_currency',
    'truncate_text',
    'batch_split',
    'safe_json_loads',
    'safe_json_dumps',
    'DataValidator'
]
