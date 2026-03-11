#!/usr/bin/env python3
"""
人工辅助选品工具

使用方式：
1. 在浏览器打开 1688 商品列表页
2. 运行 scripts/extract_1688.js 提取数据
3. 保存为 data/1688_products.json
4. 运行此脚本进行利润分析
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# 导入利润分析模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.profit_analyzer import analyze_products, parse_price_range

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def load_manual_data(input_file='data/1688_products.json'):
    """加载人工提取的数据"""
    path = Path(input_file)
    
    if not path.exists():
        logger.error(f"数据文件不存在：{input_file}")
        logger.info("\n使用指南：")
        logger.info("1. 在浏览器打开 1688 商品列表页")
        logger.info("2. 按 F12 打开开发者工具")
        logger.info("3. 在 Console 运行：scripts/extract_1688.js")
        logger.info("4. 复制输出的 JSON，保存为 data/1688_products.json")
        return None
    
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    logger.info(f"加载 {len(products)} 个商品")
    
    return products


def quick_analysis(products, min_profit_margin=0.3):
    """快速利润分析"""
    from src.profit_analyzer import analyze_product
    
    config = {
        'default_shipping_cny': 10,
        'target_profit_margin': 0.4,
        'platform_fee_rate': 0.05,
        'min_profit_margin': min_profit_margin
    }
    
    analyzed = []
    for product in products:
        result = analyze_product(product, config)
        if result:
            analyzed.append(result)
    
    # 按评分排序
    analyzed.sort(key=lambda x: x['score'], reverse=True)
    
    return analyzed


def export_results(analyzed, output_file='data/recommended_products.json'):
    """导出推荐商品"""
    recommended = [a for a in analyzed if a['recommend']]
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'total_analyzed': len(analyzed),
        'recommended_count': len(recommended),
        'products': recommended
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存推荐商品到 {output_path}")
    
    return recommended


def print_summary(analyzed, recommended):
    """打印摘要"""
    print("\n" + "=" * 60)
    print("📊 利润分析摘要")
    print("=" * 60)
    
    print(f"\n总商品数：{len(analyzed)}")
    print(f"推荐商品：{len(recommended)}")
    
    if analyzed:
        avg_margin = sum(a['profit_analysis']['profit_margin'] for a in analyzed) / len(analyzed)
        print(f"平均利润率：{avg_margin * 100:.1f}%")
    
    if recommended:
        print(f"\n🏆 TOP 5 推荐商品：")
        print("-" * 60)
        
        for i, item in enumerate(recommended[:5], 1):
            print(f"\n{i}. {item['original_product'].get('title', 'N/A')[:50]}")
            print(f"   💰 供货价：¥{item['supplier_price']:.2f}")
            print(f"   💵 建议零售价：${item['suggested_retail_price']:.2f}")
            print(f"   📈 利润率：{item['profit_analysis']['profit_margin_percent']}")
            print(f"   ⭐ 评分：{item['rating']}")
            print(f"   🔗 {item['original_product'].get('url', '')[:70]}...")


def main():
    """主函数"""
    print("\n🛒 人工辅助选品工具\n")
    print("=" * 60)
    
    # 加载数据
    products = load_manual_data()
    
    if not products:
        print("\n❌ 没有商品数据")
        print("\n快速开始：")
        print("1. 访问 1688.com")
        print("2. 搜索关键词：跨境专供、TikTok 同款、一件代发")
        print("3. 在浏览器 Console 运行：scripts/extract_1688.js")
        print("4. 保存 JSON 到 data/1688_products.json")
        print("5. 重新运行此脚本")
        return
    
    # 利润分析
    print("\n💰 进行利润分析...")
    analyzed = quick_analysis(products)
    
    if not analyzed:
        print("❌ 分析失败")
        return
    
    # 导出结果
    recommended = export_results(analyzed)
    
    # 打印摘要
    print_summary(analyzed, recommended)
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("\n下一步：")
    print("1. 查看推荐商品：data/recommended_products.json")
    print("2. 下载商品图片：python src/media_downloader.py")
    print("3. TikTok 上架：python src/tiktok_uploader.py")


if __name__ == '__main__':
    main()
