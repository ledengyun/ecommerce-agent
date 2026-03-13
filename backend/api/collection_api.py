#!/usr/bin/env python3
"""
采集任务 API 接口
支持创建异步采集任务
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from service import get_amazon_service
from utils import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["采集任务"])

# 任务状态存储（内存，生产环境应该用数据库）
collection_tasks: Dict[str, Dict] = {}


# ==================== 请求/响应模型 ====================

class CollectRequest(BaseModel):
    """采集请求"""
    keyword: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    platforms: List[str] = Field(default=['amazon'], description="采集平台列表")
    limit: int = Field(default=20, description="每个平台采集数量", ge=1, le=100)
    auto_import: bool = Field(default=True, description="是否自动导入数据库")


class CollectTaskResponse(BaseModel):
    """采集任务响应"""
    success: bool
    message: str
    task_id: str
    task_name: str
    keyword: str
    platforms: List[str]
    limit: int
    status: str
    progress: int
    created_at: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    task_name: str
    keyword: str
    platforms: List[str]
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    total_products: int
    message: str
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskStatusResponse]
    total: int


# ==================== API 端点 ====================

@router.post("/collect", response_model=CollectTaskResponse)
async def create_collection_task(request: CollectRequest, background_tasks: BackgroundTasks):
    """
    创建采集任务（异步）
    
    Args:
        keyword: 搜索关键词
        platforms: 采集平台列表 ['amazon', '1688', 'temu']
        limit: 每个平台采集数量
        auto_import: 是否自动导入数据库
        
    Returns:
        任务创建结果
    """
    try:
        # 生成任务 ID 和名称
        task_id = str(uuid.uuid4())
        task_name = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"创建采集任务：{task_id}, 关键词：{request.keyword}, 平台：{request.platforms}")
        
        # 创建任务记录
        collection_tasks[task_id] = {
            'task_id': task_id,
            'task_name': task_name,
            'keyword': request.keyword,
            'platforms': request.platforms,
            'limit': request.limit,
            'auto_import': request.auto_import,
            'status': 'pending',
            'progress': 0,
            'total_products': 0,
            'message': '任务已创建，等待执行',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'error_message': None,
            'result': None
        }
        
        # 后台执行采集任务
        background_tasks.add_task(run_collection_task, task_id)
        
        logger.info(f"采集任务已创建：{task_id}")
        
        return CollectTaskResponse(
            success=True,
            message='采集任务已创建',
            task_id=task_id,
            task_name=task_name,
            keyword=request.keyword,
            platforms=request.platforms,
            limit=request.limit,
            status='pending',
            progress=0,
            created_at=collection_tasks[task_id]['created_at']
        )
        
    except Exception as e:
        logger.error(f"创建任务失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collect/tasks", response_model=TaskListResponse)
async def get_collection_tasks(limit: int = 20):
    """
    获取采集任务列表
    
    Args:
        limit: 返回数量
        
    Returns:
        任务列表
    """
    try:
        # 按创建时间排序
        sorted_tasks = sorted(
            collection_tasks.values(),
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        
        tasks = []
        for task in sorted_tasks[:limit]:
            tasks.append(TaskStatusResponse(**task))
        
        return TaskListResponse(
            tasks=tasks,
            total=len(sorted_tasks)
        )
        
    except Exception as e:
        logger.error(f"获取任务列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collect/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务状态
    """
    if task_id not in collection_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = collection_tasks[task_id]
    return TaskStatusResponse(**task)


# ==================== 后台任务函数 ====================

def run_collection_task(task_id: str):
    """
    后台执行采集任务
    
    Args:
        task_id: 任务 ID
    """
    try:
        logger.info(f"开始执行采集任务：{task_id}")
        
        # 更新状态为运行中
        collection_tasks[task_id]['status'] = 'running'
        collection_tasks[task_id]['progress'] = 10
        collection_tasks[task_id]['message'] = '正在初始化...'
        
        task = collection_tasks[task_id]
        keyword = task['keyword']
        platforms = task['platforms']
        limit = task['limit']
        auto_import = task['auto_import']
        
        total_products = 0
        all_products = []
        
        # 遍历每个平台进行采集
        platform_count = len(platforms)
        for i, platform in enumerate(platforms):
            try:
                logger.info(f"任务 {task_id}: 采集 {platform} 平台 - {keyword}")
                
                collection_tasks[task_id]['progress'] = 10 + int((i / platform_count) * 70)
                collection_tasks[task_id]['message'] = f'正在采集 {platform} 平台...'
                
                if platform.lower() == 'amazon':
                    # 调用 Amazon 服务
                    amazon_service = get_amazon_service()
                    result = amazon_service.search_products(
                        keyword=keyword,
                        limit=limit,
                        domain='amazon.com'
                    )
                    
                    if result.get('success'):
                        products = result.get('products', [])
                        all_products.extend(products)
                        total_products += len(products)
                        logger.info(f"Amazon 采集成功：{len(products)} 个商品")
                    else:
                        logger.warning(f"Amazon 采集失败：{result.get('message')}")
                
                elif platform.lower() == '1688':
                    # TODO: 1688 采集
                    logger.info(f"1688 平台待实现")
                    collection_tasks[task_id]['message'] = f'1688 平台待实现'
                
                elif platform.lower() == 'temu':
                    # TODO: Temu 采集
                    logger.info(f"Temu 平台待实现")
                    collection_tasks[task_id]['message'] = f'Temu 平台待实现'
                
                else:
                    logger.warning(f"不支持的平台：{platform}")
                
            except Exception as e:
                logger.error(f"{platform} 采集失败：{e}")
                collection_tasks[task_id]['message'] = f'{platform} 采集失败：{str(e)}'
                continue
        
        # 导入数据库
        if auto_import and all_products:
            collection_tasks[task_id]['message'] = '正在导入数据库...'
            collection_tasks[task_id]['progress'] = 85
            
            try:
                amazon_service = get_amazon_service()
                import_result = amazon_service.import_products(all_products)
                
                if import_result.get('success'):
                    collection_tasks[task_id]['message'] = f'导入成功：{import_result.get("imported")} 个商品'
                else:
                    collection_tasks[task_id]['message'] = f'导入失败：{import_result.get("message")}'
                
            except Exception as e:
                logger.error(f"导入数据库失败：{e}")
                collection_tasks[task_id]['message'] = f'导入失败：{str(e)}'
        
        # 更新任务状态为完成
        collection_tasks[task_id]['progress'] = 100
        collection_tasks[task_id]['status'] = 'completed'
        collection_tasks[task_id]['total_products'] = total_products
        collection_tasks[task_id]['completed_at'] = datetime.now().isoformat()
        collection_tasks[task_id]['message'] = f'采集完成，共 {total_products} 个商品'
        collection_tasks[task_id]['result'] = {
            'total_products': total_products,
            'platforms_completed': platforms,
            'imported': auto_import
        }
        
        logger.info(f"采集任务完成：{task_id}, 总计 {total_products} 个商品")
        
    except Exception as e:
        logger.error(f"采集任务失败：{task_id}, 错误：{e}", exc_info=True)
        collection_tasks[task_id]['status'] = 'failed'
        collection_tasks[task_id]['error_message'] = str(e)
        collection_tasks[task_id]['message'] = f'任务失败：{str(e)}'
        collection_tasks[task_id]['completed_at'] = datetime.now().isoformat()
