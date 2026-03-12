#!/usr/bin/env python3
"""
电商选品上架 Agent - FastAPI 后端服务
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="电商选品 Agent API",
    description="电商选品上架系统的后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# 确保目录存在
for dir_path in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# 挂载静态文件
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ==================== 数据模型 ====================

class Product(BaseModel):
    id: Optional[int] = None
    title: str
    price: str
    supplier_price: Optional[str] = None
    retail_price: Optional[str] = None
    profit_margin: Optional[float] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    rating: Optional[float] = None
    recommend: Optional[bool] = None

class AnalysisRequest(BaseModel):
    keyword: Optional[str] = None
    min_profit_margin: Optional[float] = 0.3

class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None

# 任务状态存储（内存，生产环境可用 Redis）
task_status: Dict[str, TaskStatus] = {}

# ==================== API 端点 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    return {"message": "前端页面未找到，请查看 /docs 访问 API 文档"}

@app.get("/api")
async def api_root():
    """API 根路径"""
    return {
        "message": "电商选品 Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/api/status"
    }

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "available_endpoints": [
            "/api/products",
            "/api/analyze",
            "/api/recommendations",
            "/api/tasks/{task_id}"
        ]
    }

@app.get("/api/products", response_model=List[Product])
async def get_products():
    """获取所有商品数据"""
    products_file = DATA_DIR / "1688_products.json"
    
    if not products_file.exists():
        return []
    
    import json
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        return products if isinstance(products, list) else []
    except Exception as e:
        logger.error(f"读取商品数据失败：{e}")
        return []

@app.get("/api/recommendations", response_model=List[Product])
async def get_recommendations():
    """获取推荐商品"""
    recommendations_file = DATA_DIR / "recommended_products.json"
    
    if not recommendations_file.exists():
        return []
    
    import json
    try:
        with open(recommendations_file, 'r', encoding='utf-8') as f:
            recommendations = json.load(f)
        return recommendations if isinstance(recommendations, list) else []
    except Exception as e:
        logger.error(f"读取推荐数据失败：{e}")
        return []

@app.post("/api/analyze", response_model=TaskStatus)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """开始利润分析任务"""
    import uuid
    task_id = str(uuid.uuid4())
    
    task_status[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        progress=0,
        message="任务已创建，等待执行"
    )
    
    background_tasks.add_task(run_analysis_task, task_id, request)
    
    return task_status[task_id]

def run_analysis_task(task_id: str, request: AnalysisRequest):
    """后台执行利润分析任务"""
    try:
        task_status[task_id].status = "running"
        task_status[task_id].progress = 20
        task_status[task_id].message = "正在加载商品数据..."
        
        # 调用利润分析模块
        from src.manual_picker import analyze_manual_products
        
        task_status[task_id].progress = 50
        task_status[task_id].message = "正在分析利润..."
        
        result = analyze_manual_products(
            min_margin=request.min_profit_margin
        )
        
        task_status[task_id].progress = 100
        task_status[task_id].status = "completed"
        task_status[task_id].message = "分析完成"
        task_status[task_id].result = {
            "total": len(result) if isinstance(result, list) else 0,
            "recommended": sum(1 for p in result if isinstance(p, dict) and p.get('recommend', False)) if isinstance(result, list) else 0
        }
        
    except Exception as e:
        logger.error(f"分析任务失败：{e}")
        task_status[task_id].status = "failed"
        task_status[task_id].message = f"任务失败：{str(e)}"

@app.get("/api/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task_status[task_id]

@app.get("/api/stats")
async def get_stats():
    """获取统计数据"""
    import json
    
    stats = {
        "total_products": 0,
        "recommended_products": 0,
        "avg_profit_margin": 0,
        "last_updated": None
    }
    
    # 统计商品
    products_file = DATA_DIR / "1688_products.json"
    if products_file.exists():
        try:
            with open(products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                stats["total_products"] = len(products) if isinstance(products, list) else 0
        except:
            pass
    
    # 统计推荐
    rec_file = DATA_DIR / "recommended_products.json"
    if rec_file.exists():
        try:
            with open(rec_file, 'r', encoding='utf-8') as f:
                recs = json.load(f)
                if isinstance(recs, list):
                    stats["recommended_products"] = sum(1 for p in recs if p.get('recommend', False))
                    margins = [p.get('profit_margin', 0) for p in recs if p.get('profit_margin')]
                    if margins:
                        stats["avg_profit_margin"] = sum(margins) / len(margins) * 100
        except:
            pass
    
    # 最后更新时间
    if rec_file.exists():
        stats["last_updated"] = datetime.fromtimestamp(rec_file.stat().st_mtime).isoformat()
    
    return stats

@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """获取最新日志"""
    log_file = LOGS_DIR / "ecommerce_agent.log"
    
    if not log_file.exists():
        return {"logs": [], "message": "暂无日志"}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return {"logs": [line.strip() for line in recent_lines]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取日志失败：{e}")

# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
