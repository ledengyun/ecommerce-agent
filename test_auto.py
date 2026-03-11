#!/usr/bin/env python3
"""
自动化测试脚本 - 无需交互

用法：
    python test_auto.py
"""

import sys
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_collection():
    """测试商品采集"""
    print("=" * 60)
    print("📦 测试 1: 1688 商品采集")
    print("=" * 60)
    
    try:
        from src.alibaba_scraper import scrape_1688_products
        
        products = scrape_1688_products(
            keywords=['跨境专供', '一件代发'],
            limit=5,
            use_mobile=True
        )
        
        if products:
            print(f"\n✅ 成功采集 {len(products)} 个商品\n")
            for i, p in enumerate(products, 1):
                print(f"{i}. {p.get('title', 'N/A')[:60]}")
                print(f"   价格：{p.get('price', 'N/A')}")
                print()
            return True
        else:
            print("❌ 未采集到商品")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_profit_analysis():
    """测试利润分析"""
    print("\n" + "=" * 60)
    print("💰 测试 2: 利润分析")
    print("=" * 60)
    
    try:
        from src.profit_analyzer import analyze_products
        
        results = analyze_products()
        
        if results:
            print(f"\n✅ 分析了 {len(results)} 个商品")
            print(f"推荐商品：{sum(1 for r in results if r['recommend'])} 个")
            
            # 显示 TOP 3
            print("\n🏆 TOP 3 推荐:")
            for i, item in enumerate(results[:3], 1):
                print(f"\n{i}. {item['original_product'].get('title', 'N/A')[:50]}")
                print(f"   供货价：¥{item['supplier_price']:.2f}")
                print(f"   建议零售价：${item['suggested_retail_price']:.2f}")
                print(f"   利润率：{item['profit_analysis']['profit_margin_percent']}")
            
            return True
        else:
            print("❌ 没有可分析的商品")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n🧪 电商选品 Agent - 自动化测试\n")
    
    results = []
    
    # 运行测试
    print("开始采集测试（这可能需要几分钟）...\n")
    results.append(("商品采集", test_collection()))
    results.append(("利润分析", test_profit_analysis()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 测试结果")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，查看上方日志")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    main()
