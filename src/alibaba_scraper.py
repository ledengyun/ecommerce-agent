#!/usr/bin/env python3
"""
1688 商品采集模块 - 修复版

使用正确的 OpenClaw CLI 参数格式
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Alibaba1688Scraper:
    """1688 商品采集器 - 增强版"""
    
    def __init__(self, use_mobile=True):
        """
        Args:
            use_mobile: 是否使用移动端页面（反爬较松）
        """
        self.use_mobile = use_mobile
        self.base_url = "https://m.1688.com" if use_mobile else "https://www.1688.com"
        self.products = []
        self.browser_target = None
    
    def run_browser_cmd(self, action: str, *args, **kwargs) -> Optional[dict]:
        """
        执行 OpenClaw browser 命令
        
        正确的 CLI 格式：
        - openclaw browser open <url>
        - openclaw browser snapshot --format aria --target-id <id>
        - openclaw browser evaluate --fn <code> --target-id <id>
        """
        cmd = ['openclaw', 'browser', action]
        
        # 添加位置参数（如 URL）
        for arg in args:
            if arg is not None:
                cmd.append(str(arg))
        
        # 添加命名参数
        for key, value in kwargs.items():
            if value is not None:
                # 转换参数名：targetId → --target-id
                flag = f'--{key.replace("_", "-")}'
                cmd.append(flag)
                if value is not True:
                    cmd.append(str(value))
        
        try:
            logger.debug(f"执行命令：{' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    # 尝试解析 JSON
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        logger.debug(f"非 JSON 输出：{result.stdout[:200]}")
                        return {'output': result.stdout}
                return None
            else:
                logger.error(f"Browser 命令失败：{result.stderr.strip()}")
                return None
        except Exception as e:
            logger.error(f"执行命令出错：{e}")
            return None
    
    def open_page(self, url: str) -> Optional[dict]:
        """打开页面"""
        logger.info(f"打开：{url}")
        # open 命令 URL 是位置参数
        result = self.run_browser_cmd('open', url)
        if result:
            self.browser_target = result.get('targetId')
            if not self.browser_target:
                # 尝试从输出中提取
                pass
        return result
    
    def wait(self, seconds: int):
        """等待"""
        logger.info(f"等待 {seconds} 秒...")
        time.sleep(seconds)
    
    def snapshot(self, format='ai') -> Optional[dict]:
        """获取页面快照"""
        logger.info(f"获取页面快照 (format={format})...")
        return self.run_browser_cmd(
            'snapshot', 
            format=format,
            targetId=self.browser_target
        )
    
    def click(self, ref: str):
        """点击元素"""
        logger.info(f"点击：{ref}")
        return self.run_browser_cmd('click', ref, targetId=self.browser_target)
    
    def type_text(self, ref: str, text: str):
        """输入文本"""
        logger.info(f"输入：{text}")
        return self.run_browser_cmd('type', ref, text=text, targetId=self.browser_target)
    
    def evaluate(self, js_code: str) -> Optional[any]:
        """执行 JavaScript"""
        logger.info("执行 JavaScript...")
        return self.run_browser_cmd(
            'evaluate',
            fn=js_code,
            targetId=self.browser_target
        )
    
    def extract_products_manual(self) -> List[dict]:
        """
        手动提取商品信息
        
        通过执行 JavaScript 直接获取页面数据
        """
        logger.info("执行 JS 提取商品数据...")
        
        # 1688 商品列表页的通用提取脚本
        extract_js = """
        () => {
            const products = [];
            
            // 尝试多种选择器
            const selectors = [
                '.offer-item',
                '.product-item',
                '[data-role="offer-item"]',
                '.m-offer-item',
                '.search-result-offer',
                '.item-mod',
                '.dp-offer-item'
            ];
            
            let items = [];
            for (const selector of selectors) {
                items = document.querySelectorAll(selector);
                if (items.length > 0) {
                    console.log('找到选择器:', selector, '数量:', items.length);
                    break;
                }
            }
            
            if (items.length === 0) {
                console.log('未找到商品元素，页面结构可能已变化');
                return { debug: true, message: 'No products found' };
            }
            
            items.forEach((item, index) => {
                try {
                    const titleEl = item.querySelector('.title, .product-title, h2, h3, .name, .offer-title');
                    const priceEl = item.querySelector('.price, .current-price, .sale-price, .money, .price-info');
                    const salesEl = item.querySelector('.sales, .sold, .month-sales, .deal-count, .sold-count');
                    const imageEl = item.querySelector('img');
                    const linkEl = item.querySelector('a');
                    
                    const product = {
                        index: index + 1,
                        title: titleEl?.textContent?.trim() || '',
                        price: priceEl?.textContent?.trim() || '',
                        sales: salesEl?.textContent?.trim() || '',
                        image: imageEl?.src || '',
                        url: linkEl?.href || '',
                        platform: '1688'
                    };
                    
                    if (product.title) {
                        products.push(product);
                    }
                } catch (e) {
                    console.error('提取商品失败:', e);
                }
            });
            
            console.log('提取到商品数量:', products.length);
            return products;
        }
        """
        
        result = self.evaluate(extract_js)
        
        if result:
            if isinstance(result, dict) and result.get('debug'):
                logger.warning("未能提取商品：" + result.get('message', 'Unknown'))
                return []
            
            if isinstance(result, list):
                logger.info(f"提取到 {len(result)} 个商品")
                return result
        
        return []
    
    def search_products(self, keyword: str, limit: int = 10) -> List[dict]:
        """
        搜索商品
        """
        logger.info(f"搜索关键词：{keyword}")
        
        # 打开搜索页
        search_url = f"{self.base_url}/page/offerlist.html?keywords={keyword}"
        result = self.open_page(search_url)
        
        if not result:
            logger.warning("打开页面失败，尝试备用 URL")
            search_url = f"{self.base_url}/s/offer/search.html?keywords={keyword}"
            self.open_page(search_url)
        
        self.wait(5)  # 等待加载
        
        # 获取快照调试
        snapshot = self.snapshot(format='ai')
        if snapshot:
            logger.info(f"页面标题：{snapshot.get('title', 'Unknown')}")
        
        # 尝试提取
        products = self.extract_products_manual()
        
        if not products:
            logger.warning("未找到商品，尝试 aria 格式快照...")
            snapshot = self.snapshot(format='aria')
        
        return products[:limit]
    
    def scrape_by_keywords(self, keywords: List[str], limit: int = 10) -> List[dict]:
        """
        按关键词批量搜索
        """
        all_products = []
        per_keyword = max(3, limit // len(keywords))
        
        for keyword in keywords:
            if len(all_products) >= limit:
                break
            
            logger.info(f"搜索：{keyword}")
            products = self.search_products(keyword, per_keyword)
            
            # 去重
            existing_titles = {p.get('title', '') for p in all_products}
            for p in products:
                title = p.get('title', '')
                if title and title not in existing_titles:
                    all_products.append(p)
                    existing_titles.add(title)
            
            self.wait(2)
        
        return all_products[:limit]
    
    def get_hot_keywords(self) -> List[str]:
        """获取热门选品关键词"""
        return [
            '跨境专供',
            '亚马逊爆款',
            'TikTok 同款',
            '抖音网红',
            '一件代发',
            '家居好物',
            '创意小商品',
            '网红零食',
            '美妆工具',
            '手机配件',
        ]


def scrape_1688_products(
    keywords: Optional[List[str]] = None,
    limit: int = 10,
    output_file: str = 'data/1688_products.json',
    use_mobile: bool = True
) -> List[dict]:
    """
    主函数：采集 1688 商品
    """
    scraper = Alibaba1688Scraper(use_mobile=use_mobile)
    
    if keywords is None:
        keywords = scraper.get_hot_keywords()[:10]
    
    logger.info(f"开始采集，关键词：{keywords[:5]}...")
    
    products = scraper.scrape_by_keywords(keywords, limit)
    
    # 保存结果
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result_data = {
        'scraped_at': datetime.now().isoformat(),
        'platform': '1688',
        'use_mobile': use_mobile,
        'keywords': keywords,
        'total_products': len(products),
        'products': products
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 已保存 {len(products)} 个商品到 {output_path}")
    
    return products


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n🕷️  开始采集 1688 商品...\n")
    
    products = scrape_1688_products(limit=10)
    
    if products:
        print(f"\n✅ 采集完成！")
        print(f"商品数量：{len(products)}")
        print("\n前 3 个商品：")
        for i, p in enumerate(products[:3], 1):
            print(f"\n{i}. {p.get('title', 'N/A')[:60]}")
            print(f"   价格：{p.get('price', 'N/A')}")
            print(f"   销量：{p.get('sales', 'N/A')}")
    else:
        print("\n❌ 未采集到商品")
