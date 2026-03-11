#!/usr/bin/env python3
"""
利润分析模块

分析 1688 商品的利润空间，计算建议零售价
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def parse_price_range(price_str: str) -> Dict[str, float]:
    """
    解析 1688 价格区间
    
    Args:
        price_str: 价格字符串，如 "¥10.50-15.80" 或 "10.50 ~ 15.80"
    
    Returns:
        dict: {'min': 10.50, 'max': 15.80, 'currency': 'CNY'}
    """
    if not price_str:
        return {'min': 0, 'max': 0, 'currency': 'CNY'}
    
    # 移除货币符号
    price_str = price_str.replace('¥', '').replace('￥', '').replace('$', '').strip()
    
    # 检测货币
    currency = 'CNY'
    if '$' in price_str:
        currency = 'USD'
    
    # 提取数字
    numbers = re.findall(r'\d+\.?\d*', price_str)
    
    if len(numbers) >= 2:
        return {
            'min': float(numbers[0]),
            'max': float(numbers[1]),
            'currency': currency
        }
    elif len(numbers) == 1:
        val = float(numbers[0])
        return {
            'min': val,
            'max': val,
            'currency': currency
        }
    else:
        return {'min': 0, 'max': 0, 'currency': currency}


def calculate_profit(
    supplier_price: float,
    retail_price: float,
    shipping_cost: float = 0,
    platform_fee_rate: float = 0.05,
    marketing_cost: float = 0
) -> Dict:
    """
    计算利润
    
    Args:
        supplier_price: 供货价（人民币）
        retail_price: 零售价（美元）
        shipping_cost: 单件运费（人民币）
        platform_fee_rate: 平台佣金比例（默认 5%）
        marketing_cost: 营销成本（美元）
    
    Returns:
        dict: 利润分析结果
    """
    # 汇率（CNY → USD）
    exchange_rate = 7.2
    
    # 总成本（转换为美元）
    total_cost_cny = supplier_price + shipping_cost
    total_cost_usd = total_cost_cny / exchange_rate
    
    # 平台佣金
    platform_fee = retail_price * platform_fee_rate
    
    # 总成本
    total_cost = total_cost_usd + platform_fee + marketing_cost
    
    # 利润
    profit = retail_price - total_cost
    profit_margin = profit / retail_price if retail_price > 0 else 0
    
    return {
        'supplier_price_cny': round(supplier_price, 2),
        'supplier_price_usd': round(supplier_price / exchange_rate, 2),
        'shipping_cost_cny': round(shipping_cost, 2),
        'shipping_cost_usd': round(shipping_cost / exchange_rate, 2),
        'retail_price_usd': round(retail_price, 2),
        'platform_fee_usd': round(platform_fee, 2),
        'total_cost_usd': round(total_cost, 2),
        'profit_usd': round(profit, 2),
        'profit_margin': round(profit_margin, 4),
        'profit_margin_percent': f"{profit_margin * 100:.1f}%",
        'is_profitable': profit_margin > 0.3,  # 30% 利润率阈值
        'exchange_rate': exchange_rate
    }


def suggest_retail_price(
    supplier_price: float,
    target_margin: float = 0.4,
    shipping_cost: float = 10,
    platform_fee_rate: float = 0.05
) -> float:
    """
    根据供货价和目标利润率，建议零售价
    
    Args:
        supplier_price: 供货价（人民币）
        target_margin: 目标利润率（默认 40%）
        shipping_cost: 运费（人民币）
        platform_fee_rate: 平台佣金比例
    
    Returns:
        float: 建议零售价（美元）
    """
    exchange_rate = 7.2
    
    # 成本（美元）
    cost_usd = (supplier_price + shipping_cost) / exchange_rate
    
    # 考虑平台佣金，计算零售价
    # retail_price * (1 - fee_rate) - cost = profit
    # profit / retail_price = target_margin
    # retail_price = cost / (1 - fee_rate - target_margin)
    
    denominator = 1 - platform_fee_rate - target_margin
    if denominator <= 0:
        logger.warning("目标利润率过高，无法计算")
        return 0
    
    retail_price = cost_usd / denominator
    
    # 向上取整到 .99
    retail_price = round(retail_price + 0.99, 0)
    
    return retail_price


def analyze_product(product: Dict, config: Dict = None) -> Dict:
    """
    分析单个商品的利润
    
    Args:
        product: 商品数据
        config: 配置（运费、目标利润率等）
    
    Returns:
        dict: 分析结果
    """
    if config is None:
        config = {
            'default_shipping_cny': 10,  # 默认运费 10 元
            'target_profit_margin': 0.4,  # 目标利润率 40%
            'platform_fee_rate': 0.05,    # 平台佣金 5%
            'min_profit_margin': 0.3      # 最低利润率 30%
        }
    
    # 解析价格
    price_info = parse_price_range(product.get('price', ''))
    supplier_price = price_info['min']  # 取最低价
    
    if supplier_price <= 0:
        logger.warning(f"商品价格无效：{product.get('price')}")
        return None
    
    # 建议零售价
    suggested_price = suggest_retail_price(
        supplier_price,
        target_margin=config['target_profit_margin'],
        shipping_cost=config['default_shipping_cny'],
        platform_fee_rate=config['platform_fee_rate']
    )
    
    # 计算利润
    profit_info = calculate_profit(
        supplier_price=supplier_price,
        retail_price=suggested_price,
        shipping_cost=config['default_shipping_cny'],
        platform_fee_rate=config['platform_fee_rate']
    )
    
    # 综合评分
    score = 0
    if profit_info['profit_margin'] > 0.5:
        score += 3
    elif profit_info['profit_margin'] > 0.4:
        score += 2
    elif profit_info['profit_margin'] > 0.3:
        score += 1
    
    # 低价商品加分（容易出单）
    if supplier_price < 20:
        score += 2
    elif supplier_price < 50:
        score += 1
    
    return {
        'original_product': product,
        'supplier_price': supplier_price,
        'price_range': f"¥{price_info['min']:.2f} - ¥{price_info['max']:.2f}",
        'suggested_retail_price': suggested_price,
        'profit_analysis': profit_info,
        'score': score,
        'rating': '⭐⭐⭐⭐⭐' if score >= 5 else ('⭐⭐⭐⭐' if score >= 4 else ('⭐⭐⭐' if score >= 3 else '⭐⭐')),
        'recommend': profit_info['profit_margin'] > config['min_profit_margin']
    }


def analyze_products(
    input_file: str = 'data/1688_products.json',
    output_file: str = 'data/analyzed_products.json',
    config: Dict = None
) -> List[Dict]:
    """
    批量分析商品利润
    
    Args:
        input_file: 输入文件（1688 采集结果）
        output_file: 输出文件（分析结果）
        config: 配置
    
    Returns:
        list: 分析结果列表
    """
    if config is None:
        config = {
            'default_shipping_cny': 10,
            'target_profit_margin': 0.4,
            'platform_fee_rate': 0.05,
            'min_profit_margin': 0.3
        }
    
    # 加载商品数据
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"输入文件不存在：{input_file}")
        logger.info("请先运行采集：python src/alibaba_scraper.py")
        return []
    
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    logger.info(f"加载 {len(products)} 个商品")
    
    # 分析每个商品
    analyzed = []
    for product in products:
        result = analyze_product(product, config)
        if result:
            analyzed.append(result)
    
    # 按评分排序
    analyzed.sort(key=lambda x: x['score'], reverse=True)
    
    # 保存结果
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'analyzed_at': datetime.now().isoformat(),
        'total_products': len(analyzed),
        'recommended_count': sum(1 for a in analyzed if a['recommend']),
        'config': config,
        'products': analyzed
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 已保存分析结果到 {output_path}")
    
    # 打印摘要
    if analyzed:
        print(f"\n📊 利润分析摘要")
        print(f"=" * 60)
        print(f"总商品数：{len(analyzed)}")
        print(f"推荐商品：{output_data['recommended_count']}")
        
        avg_margin = sum(a['profit_analysis']['profit_margin'] for a in analyzed) / len(analyzed)
        print(f"平均利润率：{avg_margin * 100:.1f}%")
        
        print(f"\n🏆 TOP 3 推荐商品：")
        for i, item in enumerate(analyzed[:3], 1):
            print(f"\n{i}. {item['original_product'].get('title', 'N/A')[:50]}")
            print(f"   供货价：¥{item['supplier_price']:.2f}")
            print(f"   建议零售价：${item['suggested_retail_price']:.2f}")
            print(f"   利润率：{item['profit_analysis']['profit_margin_percent']}")
            print(f"   评分：{item['rating']}")
    
    return analyzed


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n💰 开始利润分析...\n")
    
    results = analyze_products()
    
    if not results:
        print("\n❌ 没有可分析的商品")
        print("提示：先运行采集脚本 python src/alibaba_scraper.py")
