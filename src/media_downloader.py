#!/usr/bin/env python3
"""
Step 3: 商品素材下载模块
下载商品图片（轮播图）
"""

import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


async def download_image(image_url, save_path):
    """
    下载单张图片
    
    使用 OpenClaw browser 工具或 requests 下载
    """
    # TODO: 实现图片下载逻辑
    # 可以使用 browser 工具截图，或用 requests 直接下载
    
    logger.info(f"下载图片：{image_url}")
    logger.warning("⚠️  图片下载需要实现具体逻辑")
    
    return save_path


async def download_product_images(matches_path='data/supplier_matches.json', 
                                   config_path='config/settings.yaml'):
    """
    主函数：下载所有匹配商品的图片
    
    Args:
        matches_path: 供应商匹配结果文件路径
        config_path: 配置文件路径
    """
    import yaml
    
    # 加载匹配结果
    matches_file = Path(matches_path)
    if not matches_file.exists():
        logger.error(f"匹配结果文件不存在：{matches_file}")
        logger.info("请先运行 Step 2: supplier_finder.py")
        return
    
    with open(matches_file, encoding='utf-8') as f:
        matches = json.load(f)
    
    # 加载配置
    config_file = Path(config_path)
    if config_file.exists():
        config = yaml.safe_load(config_file.open())
    else:
        config = {'media': {'images_per_product': 5, 'output_dir': 'output/product_images'}}
    
    output_dir = Path(config.get('media', {}).get('output_dir', 'output/product_images'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_count = 0
    
    for match in matches:
        product_id = match.get('source_product', {}).get('product_id', 'unknown')
        product_title = match.get('source_product', {}).get('title', 'unknown')[:30]
        
        # 创建商品目录
        product_dir = output_dir / f"{product_id}_{product_title.replace('/', '_')}"
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取图片 URLs
        source_images = match.get('source_product', {}).get('image_urls', [])
        supplier_images = match.get('supplier_product', {}).get('image_urls', [])
        
        all_images = list(set(source_images + supplier_images))
        max_images = config.get('media', {}).get('images_per_product', 5)
        
        # 下载图片
        for i, img_url in enumerate(all_images[:max_images]):
            save_path = product_dir / f"image_{i+1}.jpg"
            await download_image(img_url, save_path)
            downloaded_count += 1
        
        logger.info(f"商品 '{product_title}' 下载 {min(len(all_images), max_images)} 张图片")
    
    logger.info(f"✅ 总计下载 {downloaded_count} 张图片到 {output_dir}")
    
    # 保存下载记录
    record_file = output_dir / 'download_log.json'
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump({
            'downloaded_at': datetime.now().isoformat(),
            'total_images': downloaded_count,
            'products_count': len(matches)
        }, f, indent=2)


if __name__ == '__main__':
    asyncio.run(download_product_images())
