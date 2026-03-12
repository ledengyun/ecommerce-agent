-- 更新数据库表结构
USE ecommerce_agent;

-- 添加分析相关字段（如果不存在）
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS analyzed BOOLEAN DEFAULT FALSE COMMENT '是否已分析',
ADD COLUMN IF NOT EXISTS sales_volume VARCHAR(50) COMMENT '当前销售量',
ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP NULL COMMENT '最后分析时间';

-- 创建分析历史表
CREATE TABLE IF NOT EXISTS analysis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    total_products INT DEFAULT 0,
    recommended_count INT DEFAULT 0,
    avg_profit_margin DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析历史表';

-- 更新现有商品为已分析状态
UPDATE products SET analyzed = TRUE WHERE profit_margin IS NOT NULL;
