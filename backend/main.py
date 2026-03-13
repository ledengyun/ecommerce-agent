#!/usr/bin/env python3
"""
电商选品 Agent - FastAPI 后端服务（重构版）

分层架构:
- config: 配置层
- api: API 接口层
- service: 业务逻辑层
- dao: 数据访问层
- utils: 工具层
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# 导入配置
from config import (
    PROJECT_ROOT,
    DATA_DIR,
    LOGS_DIR,
    SERVER_CONFIG,
    CORS_CONFIG,
    LOGGING_CONFIG,
    FEATURE_FLAGS
)

# 导入 API 路由
from api import amazon_router, collection_router

# 导入工具
from utils import get_db

# ==================== 配置日志 ====================

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file']),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logging()

# ==================== 初始化 FastAPI 应用 ====================

app = FastAPI(
    title="电商选品 Agent API",
    description="电商选品上架系统的后端 API（重构版）",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG['allow_origins'],
    allow_credentials=CORS_CONFIG['allow_credentials'],
    allow_methods=CORS_CONFIG['allow_methods'],
    allow_headers=CORS_CONFIG['allow_headers']
)

# ==================== 挂载静态文件 ====================

FRONTEND_DIR = PROJECT_ROOT / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    logger.info(f"静态文件目录：{FRONTEND_DIR}")

# ==================== 注册 API 路由 ====================

# 采集任务（统一入口）
app.include_router(collection_router)

# Amazon 采集（直接调用）
app.include_router(amazon_router)

# 其他路由将在后续添加
# app.include_router(temu_router)
# app.include_router(1688_router)
# app.include_router(product_router)
# app.include_router(analysis_router)

# ==================== API 端点 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    
    amazon_page = FRONTEND_DIR / "amazon_collect.html"
    if amazon_page.exists():
        return amazon_page.read_text(encoding='utf-8')
    
    return {
        "message": "电商选品 Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "/api/status"
    }


@app.get("/api/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # 检查数据库连接
        db = get_db()
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "features": FEATURE_FLAGS
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ==================== 错误处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常：{exc}", exc_info=True)
    
    return {
        "success": False,
        "message": f"服务器错误：{str(exc)}",
        "path": request.url.path
    }


# ==================== 生命周期事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("="*60)
    logger.info("  电商选品 Agent API 启动")
    logger.info("="*60)
    logger.info(f"服务地址：http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    logger.info(f"环境：{'开发' if SERVER_CONFIG['debug'] else '生产'}")
    logger.info(f"数据目录：{DATA_DIR}")
    logger.info(f"日志目录：{LOGS_DIR}")
    
    # 验证配置
    try:
        from config import validate_config
        validate_config()
        logger.info("✅ 配置验证通过")
    except Exception as e:
        logger.error(f"❌ 配置验证失败：{e}")
    
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭服务...")
    
    # 关闭数据库连接
    try:
        from utils import db_manager
        db_manager.close()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库失败：{e}")
    
    logger.info("服务已关闭")


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        reload=SERVER_CONFIG['reload'],
        log_level=LOGGING_CONFIG['level'].lower()
    )
