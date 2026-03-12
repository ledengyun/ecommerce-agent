-- 创建采集任务表
CREATE TABLE IF NOT EXISTS collection_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL COMMENT '任务 ID',
    task_name VARCHAR(50) NOT NULL COMMENT '任务名称（10 位随机字符串）',
    keyword VARCHAR(200) COMMENT '搜索关键词',
    platforms VARCHAR(100) COMMENT '采集平台（JSON 数组）',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending/running/completed/failed',
    progress INT DEFAULT 0 COMMENT '进度 0-100',
    total_products INT DEFAULT 0 COMMENT '采集商品总数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采集任务表';
