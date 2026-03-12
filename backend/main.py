#!/usr/bin/env python3
"""
电商选品上架 Agent - FastAPI 后端服务 (MySQL 版) - 支持分析状态
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

import pymysql
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="电商选品 Agent API",
    description="电商选品上架系统的后端 API",
    version="1.1.0"
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

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'EcommerceAgent2026!',
    'database': 'ecommerce_agent',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )

# ==================== 数据模型 ====================

class AnalysisRequest(BaseModel):
    product_ids: Optional[List[int]] = None  # 用户选择的商品 ID，为空则自动选择
    min_profit_margin: Optional[float] = 0.3
    keyword: Optional[str] = None  # 采集关键词
    platforms: Optional[List[str]] = None  # 采集平台
    limit: Optional[int] = 20  # 采集数量

class AnalysisResult(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict[str, Any]] = None

# 任务状态存储
task_status: Dict[str, Any] = {}

# ==================== API 端点 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    return {"message": "前端页面未找到"}

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "database": db_status
    }

@app.get("/api/stats")
async def get_stats():
    """获取统计数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_products,
                SUM(CASE WHEN analyzed = TRUE THEN 1 ELSE 0 END) as analyzed_count,
                SUM(CASE WHEN analyzed = FALSE THEN 1 ELSE 0 END) as unanalyzed_count,
                SUM(CASE WHEN recommend = TRUE THEN 1 ELSE 0 END) as recommended_count,
                AVG(CASE WHEN analyzed = TRUE THEN profit_margin ELSE NULL END) as avg_profit_margin
            FROM products
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "total_products": result['total_products'] or 0,
            "analyzed_count": result['analyzed_count'] or 0,
            "unanalyzed_count": result['unanalyzed_count'] or 0,
            "recommended_count": result['recommended_count'] or 0,
            "avg_profit_margin": float(result['avg_profit_margin']) * 100 if result and result['avg_profit_margin'] else 0
        }
    except Exception as e:
        logger.error(f"获取统计失败：{e}")
        return {
            "total_products": 0,
            "analyzed_count": 0,
            "unanalyzed_count": 0,
            "recommended_count": 0,
            "avg_profit_margin": 0
        }

@app.get("/api/products/unanalyzed")
async def get_unanalyzed_products(limit: int = 50):
    """获取未分析的商品列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, supplier_price, sales_volume, image_url, source_url
            FROM products 
            WHERE analyzed = FALSE OR analyzed IS NULL
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = []
        for row in results:
            products.append({
                "id": row["id"],
                "title": row["title"],
                "supplier_price": f"¥{row['supplier_price']:.2f}" if row["supplier_price"] else (row.get('price') or '-'),
                "sales_volume": row["sales_volume"] or "未知",
                "image_url": row["image_url"],
                "source_url": row["source_url"]
            })
        
        return products
    except Exception as e:
        logger.error(f"获取未分析商品失败：{e}")
        return []

@app.get("/api/products/analyzed")
async def get_analyzed_products(limit: int = 50):
    """获取已分析的商品列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, supplier_price, retail_price, profit_margin, 
                   image_url, source_url, recommend, last_analyzed_at
            FROM products 
            WHERE analyzed = TRUE
            ORDER BY profit_margin DESC
            LIMIT %s
        """, (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = []
        for row in results:
            products.append({
                "id": row["id"],
                "title": row["title"],
                "supplier_price": f"¥{row['supplier_price']:.2f}" if row["supplier_price"] else '-',
                "retail_price": f"${row['retail_price']:.2f}" if row["retail_price"] else '-',
                "profit_margin": float(row["profit_margin"]) * 100 if row["profit_margin"] else 0,
                "recommend": bool(row["recommend"]),
                "image_url": row["image_url"],
                "source_url": row["source_url"],
                "last_analyzed_at": row["last_analyzed_at"].isoformat() if row["last_analyzed_at"] else None
            })
        
        return products
    except Exception as e:
        logger.error(f"获取已分析商品失败：{e}")
        return []

@app.post("/api/analyze", response_model=AnalysisResult)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """开始利润分析任务"""
    import uuid
    task_id = str(uuid.uuid4())
    
    # 确定要分析的商品
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.product_ids and len(request.product_ids) > 0:
        # 用户选择了商品（可以是已分析或未分析的）
        product_ids = request.product_ids
        cursor.execute("""
            SELECT id, supplier_price, sales_volume, analyzed 
            FROM products 
            WHERE id IN %s
        """, (tuple(product_ids),))
        products_to_analyze = cursor.fetchall()
        
        # 检查是否有已分析的商品
        reanalyze_count = sum(1 for p in products_to_analyze if p['analyzed'])
        if reanalyze_count > 0:
            logger.info(f"重新分析 {reanalyze_count} 个已分析商品")
    else:
        # 自动选择未分析的商品（最多 10 个）
        cursor.execute("""
            SELECT id, supplier_price, sales_volume, analyzed
            FROM products 
            WHERE analyzed = FALSE OR analyzed IS NULL
            LIMIT 10
        """)
        products_to_analyze = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not products_to_analyze:
        return AnalysisResult(
            task_id=task_id,
            status="completed",
            progress=100,
            message="没有可分析的商品",
            result={"total": 0, "analyzed": 0}
        )
    
    # 创建任务
    task_status[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "message": "任务已创建，等待执行",
        "product_ids": [p["id"] for p in products_to_analyze],
        "result": None
    }
    
    background_tasks.add_task(run_analysis_task, task_id, request)
    
    return AnalysisResult(
        task_id=task_id,
        status="pending",
        progress=0,
        message="任务已创建，等待执行",
        result=None
    )

def run_analysis_task(task_id: str, request: AnalysisRequest):
    """后台执行利润分析任务"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        task_status[task_id]["status"] = "running"
        task_status[task_id]["progress"] = 20
        task_status[task_id]["message"] = "正在分析商品..."
        
        product_ids = task_status[task_id]["product_ids"]
        
        # 分析每个商品
        for i, product_id in enumerate(product_ids):
            # 计算利润
            cursor.execute("""
                SELECT supplier_price, sales_volume FROM products WHERE id = %s
            """, (product_id,))
            product = cursor.fetchone()
            
            if product and product["supplier_price"]:
                supplier_price = float(product["supplier_price"])
                suggested_retail = supplier_price * 3.5
                estimated_cost = supplier_price + 5
                profit = suggested_retail - estimated_cost
                profit_margin = profit / suggested_retail if suggested_retail > 0 else 0
                recommend = profit_margin >= (request.min_profit_margin or 0.3)
                
                # 更新商品
                cursor.execute("""
                    UPDATE products 
                    SET analyzed = TRUE,
                        retail_price = %s,
                        profit_margin = %s,
                        recommend = %s,
                        last_analyzed_at = NOW()
                    WHERE id = %s
                """, (suggested_retail, profit_margin, recommend, product_id))
            
            # 更新进度
            task_status[task_id]["progress"] = 20 + int((i + 1) / len(product_ids) * 70)
            task_status[task_id]["message"] = f"已分析 {i+1}/{len(product_ids)} 个商品"
        
        conn.commit()
        
        # 获取统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN recommend = TRUE THEN 1 ELSE 0 END) as recommended,
                AVG(profit_margin) as avg_margin
            FROM products 
            WHERE analyzed = TRUE
        """)
        stats = cursor.fetchone()
        
        task_status[task_id]["progress"] = 100
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["message"] = "分析完成"
        task_status[task_id]["result"] = {
            "total": len(product_ids),
            "analyzed": len(product_ids),
            "recommended": stats['recommended'] if stats else 0,
            "avg_margin": float(stats['avg_margin']) * 100 if stats and stats['avg_margin'] else 0
        }
        
        logger.info(f"分析完成：{len(product_ids)}个商品")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"分析任务失败：{e}")
        task_status[task_id]["status"] = "failed"
        task_status[task_id]["message"] = f"任务失败：{str(e)}"

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_status[task_id]
    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "result": task["result"]
    }

@app.post("/api/collect")
async def collect_products(request: AnalysisRequest):
    """采集多平台商品数据"""
    try:
        import sys
        from pathlib import Path
        
        # 添加项目根目录到 Python 路径
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from src.data_collector import DataCollector
        
        keyword = request.keyword or 'home goods'
        platforms = ['1688', 'temu']  # 默认采集这两个平台
        limit = 20
        
        collector = DataCollector()
        results = collector.collect(
            keyword=keyword,
            platforms=platforms,
            limit_per_platform=limit,
            output_file='data/collected_products.json'
        )
        
        return {
            'success': True,
            'keyword': keyword,
            'platforms': platforms,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"采集失败：{e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/latest")
async def get_latest_analysis():
    """获取最近一次分析结果"""
    try:
        # 从 task_status 中获取最近完成的任务
        completed_tasks = [
            t for t in task_status.values() 
            if t["status"] == "completed" and t["result"]
        ]
        
        if not completed_tasks:
            return {
                "has_result": False,
                "message": "暂无分析结果"
            }
        
        # 获取最近的一个
        latest = completed_tasks[-1]
        
        return {
            "has_result": True,
            "task_id": latest["task_id"],
            "total_analyzed": latest["result"].get("total", 0),
            "recommended_count": latest["result"].get("recommended", 0),
            "avg_profit_margin": latest["result"].get("avg_margin", 0),
            "message": f"分析了 {latest['result'].get('total', 0)} 个商品，推荐 {latest['result'].get('recommended', 0)} 个"
        }
        
    except Exception as e:
        logger.error(f"获取最近分析结果失败：{e}")
        return {
            "has_result": False,
            "message": "获取失败"
        }

# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
