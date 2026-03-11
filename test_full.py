#!/usr/bin/env python3
"""
综合测试脚本 - 测试采集 + 利润分析

用法：
    python test_full.py
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
                print(f"   链接：{p.get('url', 'N/A')[:60]}...")
                print()
            return True
        else:
            print("❌ 未采集到商品")
            print("可能原因：")
            print("1. 网络无法访问 1688.com")
            print("2. openclaw CLI 不可用")
            print("3. 页面结构变化，需要调整选择器")
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
                print(f"   评分：{item['rating']}")
            
            return True
        else:
            print("❌ 没有可分析的商品")
            print("提示：先运行采集测试")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_parser():
    """测试价格解析"""
    print("\n" + "=" * 60)
    print("🧮 测试 3: 价格解析器")
    print("=" * 60)
    
    from src.profit_analyzer import parse_price_range
    
    test_cases = [
        "¥10.50-15.80",
        "￥20-30",
        "$5.99-9.99",
        "100",
        "¥ 50.00",
    ]
    
    all_passed = True
    for price_str in test_cases:
        result = parse_price_range(price_str)
        print(f"输入：{price_str:15} → ¥{result['min']:.2f} - ¥{result['max']:.2f} ({result['currency']})")
        
        if result['min'] <= 0 and price_str.strip():
            all_passed = False
    
    return all_passed


def test_profit_calculator():
    """测试利润计算器"""
    print("\n" + "=" * 60)
    print("📊 测试 4: 利润计算器")
    print("=" * 60)
    
    from src.profit_analyzer import calculate_profit, suggest_retail_price
    
    # 测试利润计算
    print("\n示例：供货价 ¥15，计算利润...")
    profit = calculate_profit(
        supplier_price=15,
        retail_price=29.99,
        shipping_cost=10,
        platform_fee_rate=0.05
    )
    
    print(f"供货价：¥{profit['supplier_price_cny']} (${profit['supplier_price_usd']})")
    print(f"零售价：${profit['retail_price_usd']}")
    print(f"总成本：${profit['total_cost_usd']}")
    print(f"利润：${profit['profit_usd']}")
    print(f"利润率：{profit['profit_margin_percent']}")
    print(f"是否推荐：{'✅ 是' if profit['is_profitable'] else '❌ 否'}")
    
    # 测试建议零售价
    print("\n根据供货价建议零售价...")
    suggested = suggest_retail_price(supplier_price=15, target_margin=0.4)
    print(f"供货价：¥15 → 建议零售价：${suggested:.2f}")
    
    return True


def main():
    """运行所有测试"""
    print("\n🧪 电商选品 Agent - 综合测试\n")
    print("测试项目：")
    print("1. 1688 商品采集")
    print("2. 利润分析")
    print("3. 价格解析器")
    print("4. 利润计算器")
    print()
    
    input("按 Enter 开始测试...")
    
    results = []
    
    # 运行测试
    results.append(("价格解析器", test_price_parser()))
    results.append(("利润计算器", test_profit_calculator()))
    results.append(("商品采集", test_collection()))
    results.append(("利润分析", test_profit_analysis()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("🎉 所有测试通过！可以开始使用了")
        print("\n下一步：")
        print("1. 调整选品关键词：config/settings.yaml")
        print("2. 运行完整采集：python main.py --step 1")
        print("3. 查看分析结果：data/analyzed_products.json")
    else:
        print("⚠️ 部分测试失败")
        print("\n调试建议：")
        print("1. 检查 openclaw CLI: openclaw --help")
        print("2. 检查网络：能否访问 1688.com")
        print("3. 查看日志：logs/ecommerce_agent.log")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
