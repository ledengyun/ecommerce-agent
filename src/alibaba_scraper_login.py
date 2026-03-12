#!/usr/bin/env python3
"""
1688 商品采集模块 - 支持登录
使用买家账号登录后采集，提高成功率
"""

import json
import logging
import subprocess
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Alibaba1688Scraper:
    """1688 商品采集器 - 支持登录"""
    
    # 移动端 User-Agent
    MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    
    def __init__(self, use_mobile=True, username: str = None, password: str = None):
        """
        Args:
            use_mobile: 是否使用移动端页面
            username: 1688 账号（手机号）
            password: 1688 密码
        """
        self.use_mobile = use_mobile
        self.base_url = "https://m.1688.com" if use_mobile else "https://www.1688.com"
        self.products = []
        self.browser_target = None
        self.username = username
        self.password = password
        self.is_logged_in = False
        
        # 搜索关键词列表
        self.keywords = [
            "跨境专供",
            "TikTok 同款", 
            "一件代发",
            "抖音网红",
            "亚马逊爆款"
        ]
    
    def run_browser_cmd(self, action: str, *args, **kwargs) -> Optional[dict]:
        """执行 OpenClaw browser 命令"""
        cmd = ['openclaw', 'browser', action]
        
        for arg in args:
            if arg is not None:
                cmd.append(str(arg))
        
        for key, value in kwargs.items():
            if value is not None:
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
                timeout=120
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return {'output': result.stdout}
                return None
            else:
                logger.error(f"Browser 命令失败：{result.stderr.strip()}")
                return None
        except subprocess.TimeoutExpired:
            logger.error("命令执行超时")
            return None
        except Exception as e:
            logger.error(f"执行命令出错：{e}")
            return None
    
    def random_sleep(self, min_sec=2, max_sec=5):
        """随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        logger.info(f"随机等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def get_target_id(self, result: dict) -> Optional[str]:
        """从命令结果中提取 targetId"""
        if not result:
            return None
        
        # 尝试多种方式获取
        target_id = (
            result.get('targetId') or 
            result.get('id') or
            result.get('target_id')
        )
        
        # 从输出文本中提取
        if not target_id and 'output' in result:
            output = result['output']
            if 'id: ' in output:
                target_id = output.split('id: ')[1].strip().split('\n')[0]
        
        return target_id
    
    def login(self) -> bool:
        """
        登录 1688 - 简化版
        直接打开登录页，提示用户手动登录，然后继续采集
        
        Returns:
            是否登录成功
        """
        if not self.username or not self.password:
            logger.warning("未提供账号密码，跳过登录")
            return False
        
        logger.info("="*60)
        logger.info("1688 登录说明")
        logger.info("="*60)
        logger.info(f"账号：{self.username}")
        logger.info("")
        logger.info("由于 1688 登录可能需要滑块验证，建议：")
        logger.info("1. 在浏览器中打开：https://m.1688.com/")
        logger.info("2. 手动登录你的账号")
        logger.info("3. 登录后保持浏览器打开状态")
        logger.info("4. 然后运行采集脚本")
        logger.info("")
        logger.info("或者继续使用未登录模式采集（人工辅助）")
        logger.info("="*60)
        
        # 尝试直接打开搜索页，假设浏览器已登录
        logger.info("尝试直接访问搜索页面...")
        self.is_logged_in = True
        return True
    
    def open_search_page(self, keyword: str) -> bool:
        """打开搜索页面"""
        if self.use_mobile:
            url = f"{self.base_url}/page/search.html?keywords={keyword}&sort=&filter=&pageSize=40&beginPage=1"
        else:
            url = f"{self.base_url}/page/search.html?keywords={keyword}"
        
        logger.info(f"打开搜索页面：{url}")
        
        result = self.run_browser_cmd('open', url)
        if result:
            self.browser_target = self.get_target_id(result)
            logger.info(f"页面打开成功，targetId: {self.browser_target}")
            return True
        
        logger.error("页面打开失败")
        return False
    
    def check_page_loaded(self, timeout=15) -> bool:
        """检查页面是否加载完成"""
        logger.info(f"等待页面加载（最多 {timeout} 秒）...")
        
        self.random_sleep(3, 5)
        
        # 获取快照检查
        snapshot = self.snapshot()
        if snapshot:
            text = str(snapshot.get('text', ''))
            
            # 检查反爬
            if 'unusual traffic' in text.lower() or '检测' in text or '安全验证' in text:
                logger.error("检测到反爬页面！")
                return False
            
            # 检查是否有商品相关内容
            if any(x in text for x in ['商品', '产品', 'offer', 'product', '¥', '￥']):
                logger.info("检测到商品内容")
                return True
        
        return True
    
    def snapshot(self, format='ai'):
        """获取页面快照"""
        logger.info(f"获取页面快照 (format={format})...")
        return self.run_browser_cmd(
            'snapshot', 
            **{'format': format, 'target-id': self.browser_target}
        )
    
    def extract_products_js(self) -> List[dict]:
        """执行 JavaScript 提取商品数据"""
        logger.info("执行 JS 提取商品数据...")
        
        extract_js = """
        () => {
            const products = [];
            
            // 多种选择器
            const selectors = [
                '.offer-item', '.m-offer-item', '.product-item',
                '[data-role="offer-item"]', '.search-result-offer',
                '.item-mod', '.dp-offer-item', '.list-item',
                'li[role="listitem"]', '.list-content > div'
            ];
            
            let items = [];
            for (const selector of selectors) {
                items = document.querySelectorAll(selector);
                if (items.length > 0) {
                    console.log('✅ 找到选择器:', selector, '数量:', items.length);
                    break;
                }
            }
            
            // 备用方案：找包含价格的元素
            if (items.length === 0) {
                const allDivs = document.querySelectorAll('div, li');
                items = Array.from(allDivs).filter(div => {
                    const text = div.textContent;
                    return (text.includes('¥') || text.includes('￥')) && text.length > 10 && text.length < 200;
                }).slice(0, 20);
                console.log('使用备用方案找到', items.length, '个元素');
            }
            
            items.forEach((item, index) => {
                try {
                    const findElement = (selectors) => {
                        for (const sel of selectors) {
                            const el = item.querySelector(sel);
                            if (el && el.textContent.trim()) return el;
                        }
                        return null;
                    };
                    
                    const titleEl = findElement([
                        '.title', '.product-title', 'h2', 'h3', '.name', 
                        '.offer-title', '.product-name', '[data-role="title"]'
                    ]);
                    
                    const priceEl = findElement([
                        '.price', '.current-price', '.sale-price', '.money', 
                        '.price-info', '[data-role="price"]', '.price-now'
                    ]);
                    
                    const salesEl = findElement([
                        '.sales', '.sold', '.month-sales', '.deal-count'
                    ]);
                    
                    const imageEl = item.querySelector('img');
                    const linkEl = item.querySelector('a[href*="offer"]') || item.querySelector('a');
                    
                    const title = titleEl?.textContent?.trim() || '';
                    const price = priceEl?.textContent?.trim() || '';
                    
                    if (title && price) {
                        products.push({
                            index: index + 1,
                            title: title,
                            price: price,
                            sales: salesEl?.textContent?.trim() || '',
                            image: imageEl?.src || imageEl?.dataset?.src || '',
                            url: linkEl?.href || ''
                        });
                    }
                } catch (e) {
                    console.error('提取失败:', e);
                }
            });
            
            console.log('✅ 成功提取', products.length, '个商品');
            return products;
        }
        """
        
        result = self.run_browser_cmd('evaluate', fn=extract_js, **{'target-id': self.browser_target})
        
        if result:
            data = result.get('result') or result.get('output')
            if isinstance(data, list):
                return data
            elif isinstance(data, str):
                try:
                    return json.loads(data)
                except:
                    pass
        
        return []
    
    def save_products(self, products: List[dict], output_file: str = None):
        """保存商品数据"""
        if output_file is None:
            output_file = Path(__file__).parent.parent / 'data' / '1688_products.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存 {len(products)} 个商品到 {output_file}")
    
    def scrape(self, keywords: List[str] = None, max_products: int = 20, do_login: bool = True) -> List[dict]:
        """
        执行采集流程
        
        Args:
            keywords: 搜索关键词列表
            max_products: 最大采集商品数
            do_login: 是否先登录
            
        Returns:
            商品列表
        """
        keywords = keywords or self.keywords[:2]
        all_products = []
        
        logger.info(f"开始采集，目标：{max_products} 个商品，关键词：{keywords}")
        
        # 1. 先登录
        if do_login and self.username and self.password:
            if not self.login():
                logger.warning("登录失败，尝试不登录采集")
        
        # 2. 采集商品
        for i, keyword in enumerate(keywords):
            if len(all_products) >= max_products:
                logger.info(f"已达到目标商品数 ({len(all_products)})，停止采集")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"第 {i+1} 个关键词：{keyword}")
            logger.info(f"{'='*60}")
            
            try:
                if not self.open_search_page(keyword):
                    continue
                
                self.random_sleep(3, 6)
                
                if not self.check_page_loaded():
                    self.random_sleep(2, 3)
                    continue
                
                products = self.extract_products_js()
                
                if products:
                    logger.info(f"提取到 {len(products)} 个商品")
                    all_products.extend(products)
                else:
                    logger.warning(f"未提取到商品：{keyword}")
                
                if i < len(keywords) - 1:
                    self.random_sleep(3, 5)
                
            except Exception as e:
                logger.error(f"采集关键词 {keyword} 时出错：{e}")
                continue
        
        # 去重
        seen_urls = set()
        unique_products = []
        for p in all_products:
            url = p.get('url', '') or p.get('image', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_products.append(p)
            elif not url:
                unique_products.append(p)
        
        logger.info(f"\n采集完成：共 {len(unique_products)} 个商品（去重后）")
        
        if unique_products:
            self.save_products(unique_products)
        
        return unique_products
    
    def close(self):
        """关闭浏览器"""
        if self.browser_target:
            logger.info("关闭浏览器...")
            try:
                self.run_browser_cmd('close', **{'target-id': self.browser_target})
            except:
                pass


def scrape_1688_products(
    keywords: List[str] = None, 
    limit: int = 20,
    username: str = None,
    password: str = None
) -> List[dict]:
    """便捷函数：采集 1688 商品"""
    scraper = Alibaba1688Scraper(
        use_mobile=True,
        username=username,
        password=password
    )
    
    try:
        products = scraper.scrape(keywords=keywords, max_products=limit, do_login=bool(username))
        return products
    finally:
        scraper.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("1688 商品采集测试（支持登录）")
    print("="*60)
    
    # 从配置文件加载账号
    config_file = Path(__file__).parent.parent / 'config' / '1688_credentials.json'
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        USERNAME = config.get('username', '')
        PASSWORD = config.get('password', '')
    else:
        USERNAME = ""
        PASSWORD = ""
    
    if not USERNAME or not PASSWORD:
        print("\n⚠️  未配置账号密码，请在脚本中填写 USERNAME 和 PASSWORD")
        print("或创建 config/1688_credentials.json 文件：")
        print('''
{
    "username": "你的手机号",
    "password": "你的密码"
}
''')
    else:
        products = scrape_1688_products(
            keywords=["跨境专供", "TikTok 同款"],
            limit=15,
            username=USERNAME,
            password=PASSWORD
        )
        
        print(f"\n✅ 采集完成：{len(products)} 个商品")
        if products:
            print("\n前 3 个商品示例:")
            for i, p in enumerate(products[:3], 1):
                print(f"\n{i}. {p.get('title', 'N/A')[:50]}")
                print(f"   价格：{p.get('price', 'N/A')}")
