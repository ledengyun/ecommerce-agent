#!/usr/bin/env python3
"""
快速测试脚本 - 测试 1688 采集功能

用法：
    python test_1688.py
"""

import sys
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.alibaba_scraper import scrape_1688_products, Alibaba1688Scraper

def test_basic_search():
    """测试基本搜索功能"""
    print("=" * 60)
    print("测试 1: 基本关键词搜索")
    print("=" * 60)
    
    try:
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
        else:
            print("❌ 未采集到商品，可能需要调整选择器")
        
        return len(products) > 0
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_manual_extraction():
    """测试手动提取功能"""
    print("\n" + "=" * 60)
    print("测试 2: 手动页面提取")
    print("=" * 60)
    
    try:
        scraper = Alibaba1688Scraper(use_mobile=True)
        
        # 打开一个具体页面
        test_url = "https://m.1688.com/page/offerlist.html?keywords=家居好物"
        print(f"打开页面：{test_url}")
        scraper.open_page(test_url)
        
        print("等待 5 秒加载...")
        scraper.wait(5)
        
        print("提取商品...")
        products = scraper.extract_products_manual()
        
        if products:
            print(f"\n✅ 提取到 {len(products)} 个商品")
            for i, p in enumerate(products[:3], 1):
                print(f"\n{i}. {p.get('title', 'N/A')[:50]}")
                print(f"   价格：{p.get('price', 'N/A')}")
        else:
            print("❌ 未提取到商品")
            print("提示：可能需要调整 JS 选择器")
        
        return len(products) > 0
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_structure():
    """测试数据结构"""
    print("\n" + "=" * 60)
    print("测试 3: 数据结构验证")
    print("=" * 60)
    
    required_fields = ['title', 'price', 'url', 'image', 'platform']
    
    try:
        products = scrape_1688_products(limit=3, output_file='data/test_products.json')
        
        if not products:
            print("❌ 无商品数据")
            return False
        
        # 检查字段完整性
        for i, p in enumerate(products, 1):
            missing = [f for f in required_fields if f not in p]
            if missing:
                print(f"商品 {i} 缺少字段：{missing}")
            else:
                print(f"✅ 商品 {i} 数据结构完整")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n🧪 1688 采集功能测试\n")
    print("请确保：")
    print("1. 已安装依赖：pip install -r requirements.txt")
    print("2. 网络能访问 1688.com")
    print("3. 在 OpenClaw 环境中运行（需要 browser 工具）")
    print()
    
    input("按 Enter 开始测试...")
    
    results = []
    
    # 运行测试
    results.append(("基本搜索", test_basic_search()))
    # results.append(("手动提取", test_manual_extraction()))
    results.append(("数据结构", test_data_structure()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("🎉 所有测试通过！可以开始使用了")
    else:
        print("⚠️ 部分测试失败，请检查日志")
        print("\n调试建议：")
        print("1. 检查 1688 是否能正常访问")
        print("2. 查看浏览器是否打开正确页面")
        print("3. 调整 src/1688_scraper.py 中的 JS 选择器")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
