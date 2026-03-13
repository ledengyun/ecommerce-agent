#!/usr/bin/env python3
"""
统一商品导入工具
支持多种数据源：1688 JSON、Temu API、手动 CSV 等
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.auto_import import import_products_to_db, process_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('product_importer')


def import_from_json(file_path: str, platform: str = '1688') -> Dict:
    """
    从 JSON 文件导入商品
    
    Args:
        file_path: JSON 文件路径
        platform: 平台标识
        
    Returns:
        导入结果
    """
    path = Path(file_path)
    
    if not path.exists():
        return {'success': False, 'message': f'文件不存在：{file_path}'}
    
    logger.info(f"📄 导入文件：{file_path}")
    logger.info(f"🏷️  平台：{platform}")
    
    # 使用现有的 process_file 函数
    result = process_file(path)
    
    return result


def import_from_dict(products: List[Dict], platform: str = 'manual') -> Dict:
    """
    从字典列表导入商品
    
    Args:
        products: 商品数据列表
        platform: 平台标识
        
    Returns:
        导入结果
    """
    logger.info(f"📊 导入 {len(products)} 个商品，平台：{platform}")
    
    result = import_products_to_db(products, platform, truncate=False)
    
    return result


def get_latest_1688_data() -> str:
    """获取最新的 1688 数据文件"""
    data_dir = Path(__file__).parent.parent / 'data'
    files = list(data_dir.glob('1688_products*.json'))
    
    if not files:
        # 检查 processed 目录
        processed_dir = data_dir / 'processed'
        files = list(processed_dir.glob('1688_products*.json'))
    
    if files:
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='商品数据导入工具')
    parser.add_argument('--file', type=str, help='JSON 文件路径')
    parser.add_argument('--platform', type=str, default='1688', 
                       choices=['1688', 'temu', 'amazon', 'manual'],
                       help='平台标识')
    parser.add_argument('--latest', action='store_true', 
                       help='导入最新的 1688 数据')
    parser.add_argument('--truncate', action='store_true',
                       help='导入前清空数据库')
    
    args = parser.parse_args()
    
    print("="*60)
    print("  商品数据导入工具")
    print("="*60)
    print()
    
    # 确定输入文件
    file_path = None
    
    if args.file:
        file_path = args.file
    elif args.latest:
        file_path = get_latest_1688_data()
        if not file_path:
            print("❌ 未找到 1688 数据文件")
            sys.exit(1)
        print(f"📁 使用最新文件：{file_path}")
    else:
        # 默认导入最新的 1688 数据
        file_path = get_latest_1688_data()
        if file_path:
            print(f"📁 使用最新文件：{file_path}")
        else:
            print("❌ 未指定文件且未找到 1688 数据")
            print("\n用法:")
            print("  python3 src/product_importer.py --file data/products.json")
            print("  python3 src/product_importer.py --latest")
            sys.exit(1)
    
    # 导入数据
    result = import_from_json(file_path, args.platform)
    
    print()
    print("="*60)
    print("  导入结果")
    print("="*60)
    print()
    
    if result.get('success'):
        print(f"✅ 导入成功！")
        print(f"   商品数量：{result.get('imported', 0)}")
        print(f"   推荐商品：{result.get('recommended', 0)}")
        print(f"   数据库总数：{result.get('total_in_db', 0)}")
        print()
        print("📊 查看数据库:")
        print("   mysql -u root -p'EcommerceAgent2026!' -e \"SELECT * FROM ecommerce_agent.products ORDER BY id DESC LIMIT 10;\"")
    else:
        print(f"❌ 导入失败：{result.get('message', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
