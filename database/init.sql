-- 电商选品 Agent 数据库初始化脚本
-- 创建数据库和表结构

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_agent 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce_agent;

-- 商品表 (1688 商品数据)
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL COMMENT '商品标题',
    price VARCHAR(50) COMMENT '价格区间',
    supplier_price DECIMAL(10,2) COMMENT '供货价',
    retail_price DECIMAL(10,2) COMMENT '建议零售价',
    profit_margin DECIMAL(5,4) COMMENT '利润率 (0-1)',
    image_url VARCHAR(1000) COMMENT '主图 URL',
    source_url VARCHAR(500) COMMENT '商品链接',
    sales VARCHAR(50) COMMENT '销量',
    rating DECIMAL(3,2) COMMENT '评分',
    recommend BOOLEAN DEFAULT FALSE COMMENT '是否推荐',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_recommend (recommend),
    INDEX idx_profit_margin (profit_margin),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品数据表';

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL COMMENT '任务 ID',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending/running/completed/failed',
    progress INT DEFAULT 0 COMMENT '进度 (0-100)',
    message VARCHAR(500) COMMENT '任务消息',
    total_products INT DEFAULT 0 COMMENT '总商品数',
    recommended_products INT DEFAULT 0 COMMENT '推荐商品数',
    avg_profit_margin DECIMAL(5,4) COMMENT '平均利润率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析任务表';

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) DEFAULT 'INFO' COMMENT '日志级别',
    message TEXT COMMENT '日志内容',
    module VARCHAR(100) COMMENT '模块名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统日志表';

-- 配置表
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    setting_value TEXT COMMENT '配置值',
    setting_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型',
    description VARCHAR(500) COMMENT '配置说明',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 插入默认配置
INSERT INTO settings (setting_key, setting_value, setting_type, description) VALUES
('min_profit_margin', '0.3', 'float', '最低利润率阈值'),
('target_profit_margin', '0.4', 'float', '目标利润率'),
('shipping_cost', '5.0', 'float', '运费估算 (元)'),
('retail_price_multiplier', '3.5', 'float', '零售价倍率'),
('max_products_per_analysis', '100', 'int', '单次分析最大商品数');

-- 创建统计视图
CREATE OR REPLACE VIEW v_product_stats AS
SELECT 
    COUNT(*) as total_products,
    SUM(CASE WHEN recommend THEN 1 ELSE 0 END) as recommended_products,
    AVG(profit_margin) as avg_profit_margin,
    MAX(created_at) as last_updated
FROM products;

-- 创建用户（可选，用于应用连接）
-- CREATE USER IF NOT EXISTS 'ecommerce'@'localhost' IDENTIFIED BY 'EcommerceAgent2026!';
-- GRANT ALL PRIVILEGES ON ecommerce_agent.* TO 'ecommerce'@'localhost';
-- FLUSH PRIVILEGES;
