#!/usr/bin/env python3
"""
记录分析任务到数据库
"""

import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'EcommerceAgent2026!',
    'database': 'ecommerce_agent',
    'charset': 'utf8mb4'
}

def save_task(task_id, status, progress, message, total=0, recommended=0, avg_margin=None):
    """保存任务记录到数据库"""
    conn = pymysql.connect(**{k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'})
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在
        cursor.execute("SELECT id FROM analysis_tasks WHERE task_id = %s", (task_id,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            sql = """
            UPDATE analysis_tasks 
            SET status=%s, progress=%s, message=%s, 
                total_products=%s, recommended_products=%s, 
                avg_profit_margin=%s, completed_at=%s
            WHERE task_id = %s
            """
            cursor.execute(sql, (status, progress, message, total, recommended, avg_margin, 
                                datetime.now() if status == 'completed' else None, task_id))
        else:
            # 插入新记录
            sql = """
            INSERT INTO analysis_tasks 
            (task_id, status, progress, message, total_products, recommended_products, 
             avg_profit_margin, created_at, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (task_id, status, progress, message, total, recommended, 
                                avg_margin, datetime.now(),
                                datetime.now() if status == 'completed' else None))
        
        conn.commit()
        print(f"✅ 任务记录已保存：{task_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 保存任务失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # 测试
    save_task('test-001', 'completed', 100, '测试任务', 15, 15, 0.618)
