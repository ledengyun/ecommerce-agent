#!/usr/bin/env python3
"""
电商选品上架 Agent - 主入口
"""

import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ecommerce_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_pipeline():
    """执行完整流程"""
    logger.info("🚀 开始执行完整选品上架流程")
    
    # Step 1: 采集 1688 热销商品
    logger.info("📦 Step 1: 采集 1688 热销商品...")
    from src.alibaba_scraper import scrape_1688_products
    hot_products = scrape_1688_products(limit=10)
    logger.info(f"✅ 采集完成，共 {len(hot_products)} 个商品")
    
    # Step 2: 利润分析
    logger.info("💰 Step 2: 利润分析...")
    from src.profit_analyzer import analyze_products
    analyzed = analyze_products()
    logger.info(f"✅ 分析完成，推荐 {sum(1 for a in analyzed if a['recommend'])} 个商品")
    
    # Step 3: 下载商品图片
    logger.info("🖼️ Step 3: 下载商品素材...")
    from src.media_downloader import download_product_images
    download_product_images()
    logger.info("✅ 图片下载完成")
    
    # Step 4: 上架 TikTok
    logger.info("📤 Step 4: 上架商品到 TikTok...")
    from src.tiktok_uploader import upload_to_tiktok
    upload_to_tiktok()
    logger.info("✅ 上架完成")
    
    logger.info("🎉 完整流程执行完毕！")

def main():
    parser = argparse.ArgumentParser(description='电商选品上架 Agent')
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4], 
                        help='执行指定步骤 (1-4)，不指定则执行全流程')
    parser.add_argument('--config', type=str, default='config/settings.yaml',
                        help='配置文件路径')
    
    args = parser.parse_args()
    
    if args.step is None:
        run_full_pipeline()
    elif args.step == 1:
        from src.alibaba_scraper import scrape_1688_products
        scrape_1688_products()
    elif args.step == 2:
        from src.profit_analyzer import analyze_products
        analyze_products()
    elif args.step == 3:
        from src.media_downloader import download_product_images
        download_product_images()
    elif args.step == 4:
        from src.tiktok_uploader import upload_to_tiktok
        upload_to_tiktok()

if __name__ == '__main__':
    main()
