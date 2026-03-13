#!/usr/bin/env python3
"""
亚马逊采集 API 接口
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from service import get_amazon_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/amazon", tags=["Amazon 采集"])

# 请求模型
class AmazonCollectRequest(BaseModel):
    """亚马逊采集请求"""
    keyword: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    limit: int = Field(default=20, description="采集数量", ge=1, le=100)
    domain: str = Field(default='amazon.com', description="亚马逊站点")
    auto_import: bool = Field(default=True, description="是否自动导入数据库")


class AmazonTrackRequest(BaseModel):
    """亚马逊商品追踪请求"""
    asin: str = Field(..., description="商品 ASIN")
    domain: str = Field(default='amazon.com', description="亚马逊站点")


# 响应模型
class AmazonCollectResponse(BaseModel):
    """亚马逊采集响应"""
    success: bool
    message: str
    keyword: Optional[str] = None
    domain: Optional[str] = None
    total_products: int
    products: List[Dict[str, Any]]
    import_result: Optional[Dict[str, Any]] = None
    credits_remaining: Optional[int] = None


class AmazonStatusResponse(BaseModel):
    """亚马逊采集器状态响应"""
    status: str
    api_configured: bool
    api_key_prefix: Optional[str] = None
    credits_remaining: Optional[int] = None
    supported_domains: Optional[List[str]] = None


# API 端点
@router.post("/collect", response_model=AmazonCollectResponse)
async def collect_amazon(request: AmazonCollectRequest):
    """
    采集亚马逊商品
    
    Args:
        keyword: 搜索关键词
        limit: 采集数量 (1-100)
        domain: 亚马逊站点
        auto_import: 是否自动导入数据库
        
    Returns:
        采集结果
    """
    try:
        # 获取服务
        amazon_service = get_amazon_service()
        
        # 执行采集
        result = amazon_service.search_products(
            keyword=request.keyword,
            limit=request.limit,
            domain=request.domain
        )
        
        # 检查采集结果
        if not result.get('success'):
            return AmazonCollectResponse(
                success=False,
                message=result.get('message', '采集失败'),
                keyword=request.keyword,
                domain=request.domain,
                total_products=0,
                products=[],
                credits_remaining=result.get('credits_remaining')
            )
        
        # 自动导入数据库
        import_result = None
        if request.auto_import and result.get('products'):
            import_result = amazon_service.import_products(result['products'])
        
        return AmazonCollectResponse(
            success=True,
            message=result.get('message', '采集成功'),
            keyword=request.keyword,
            domain=request.domain,
            total_products=result.get('total_products', 0),
            products=result.get('products', []),
            import_result=import_result,
            credits_remaining=result.get('credits_remaining')
        )
        
    except Exception as e:
        logger.error(f"亚马逊采集 API 错误：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AmazonStatusResponse)
async def get_amazon_status():
    """获取亚马逊采集器状态"""
    try:
        amazon_service = get_amazon_service()
        status = amazon_service.check_api_status()
        
        return AmazonStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"获取状态失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{asin}")
async def get_product_details(asin: str, domain: str = 'amazon.com'):
    """
    获取商品详情
    
    Args:
        asin: 商品 ASIN
        domain: 亚马逊站点
    """
    try:
        amazon_service = get_amazon_service()
        result = amazon_service.get_product_details(asin, domain)
        
        if result.get('success'):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get('message', '未找到商品'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取商品详情失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
