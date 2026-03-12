# 📊 MySQL 数据库使用指南

## 数据库信息

| 项目 | 值 |
|------|-----|
| **数据库名** | `ecommerce_agent` |
| **主机** | `localhost` |
| **端口** | `3306` |
| **用户名** | `root` |
| **密码** | `EcommerceAgent2026!` |
| **字符集** | `utf8mb4` |

---

## 表结构

### 1. products - 商品表

存储所有采集的商品数据和利润分析结果。

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,        -- 商品标题
    price VARCHAR(50),                   -- 价格区间
    supplier_price DECIMAL(10,2),        -- 供货价
    retail_price DECIMAL(10,2),          -- 建议零售价
    profit_margin DECIMAL(5,4),          -- 利润率
    image_url VARCHAR(1000),             -- 主图 URL
    source_url VARCHAR(500),             -- 商品链接
    sales VARCHAR(50),                   -- 销量
    rating DECIMAL(3,2),                 -- 评分
    recommend BOOLEAN,                   -- 是否推荐
    created_at TIMESTAMP,                -- 创建时间
    updated_at TIMESTAMP                 -- 更新时间
);
```

### 2. analysis_tasks - 分析任务表

记录每次利润分析任务的执行状态。

```sql
CREATE TABLE analysis_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE,         -- 任务 ID
    status VARCHAR(20),                  -- pending/running/completed/failed
    progress INT,                        -- 进度 0-100
    message VARCHAR(500),                -- 任务消息
    total_products INT,                  -- 总商品数
    recommended_products INT,            -- 推荐商品数
    avg_profit_margin DECIMAL(5,4),      -- 平均利润率
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 3. system_logs - 系统日志表

存储系统运行日志。

```sql
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20),                   -- INFO/WARNING/ERROR
    message TEXT,                        -- 日志内容
    module VARCHAR(100),                 -- 模块名称
    created_at TIMESTAMP
);
```

### 4. settings - 配置表

存储系统配置参数。

```sql
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE,     -- 配置键
    setting_value TEXT,                  -- 配置值
    setting_type VARCHAR(20),            -- string/float/int
    description VARCHAR(500),            -- 配置说明
    updated_at TIMESTAMP
);
```

---

## 常用查询

### 查看统计数据
```sql
SELECT * FROM v_product_stats;
```

### 查询推荐商品（按利润率排序）
```sql
SELECT * FROM products 
WHERE recommend = TRUE 
ORDER BY profit_margin DESC 
LIMIT 20;
```

### 查询高利润商品（利润率 > 60%）
```sql
SELECT title, supplier_price, retail_price, profit_margin 
FROM products 
WHERE profit_margin > 0.6 
ORDER BY profit_margin DESC;
```

### 查看配置参数
```sql
SELECT * FROM settings;
```

### 查看最近日志
```sql
SELECT * FROM system_logs 
ORDER BY created_at DESC 
LIMIT 50;
```

---

## 命令行操作

### 登录 MySQL
```bash
mysql -u root -p'EcommerceAgent2026!'
```

### 选择数据库
```sql
USE ecommerce_agent;
```

### 导出数据
```bash
# 导出商品表
mysqldump -u root -p'EcommerceAgent2026!' ecommerce_agent products > products_backup.sql

# 导出整个数据库
mysqldump -u root -p'EcommerceAgent2026!' ecommerce_agent > ecommerce_agent_backup.sql
```

### 导入数据
```bash
mysql -u root -p'EcommerceAgent2026!' ecommerce_agent < products_backup.sql
```

---

## Python 连接示例

```python
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='EcommerceAgent2026!',
    database='ecommerce_agent',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # 查询推荐商品
        sql = "SELECT * FROM products WHERE recommend = TRUE LIMIT 10"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        for row in results:
            print(f"{row['title']}: {row['profit_margin']:.2%}")
finally:
    conn.close()
```

---

## API 端点（使用数据库）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/status` | GET | 系统状态（含数据库连接状态） |
| `/api/stats` | GET | 统计数据（从视图查询） |
| `/api/products` | GET | 商品列表（从 products 表） |
| `/api/recommendations` | GET | 推荐商品（查询 recommend=TRUE） |
| `/api/analyze` | POST | 执行分析（更新 products 表） |
| `/api/tasks/{id}` | GET | 任务状态（从 analysis_tasks 表） |

---

## 数据导入

### 从 JSON 导入
```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 database/import_data.py
```

### 重置数据
```sql
-- 清空商品表
TRUNCATE TABLE products;

-- 重置自增 ID
ALTER TABLE products AUTO_INCREMENT = 1;
```

---

## 性能优化

### 索引
已创建的索引：
- `idx_recommend` - 推荐状态索引
- `idx_profit_margin` - 利润率索引
- `idx_created_at` - 创建时间索引
- `idx_task_id` - 任务 ID 索引
- `idx_status` - 任务状态索引

### 视图
`v_product_stats` - 统计信息视图，快速查询总体数据。

---

## 安全建议

1. **修改默认密码** - 生产环境请修改 root 密码
2. **创建专用用户** - 为应用创建专用数据库用户
3. **限制远程访问** - 默认只允许 localhost 连接
4. **定期备份** - 使用 mysqldump 定期备份数据

### 创建应用专用用户
```sql
CREATE USER 'ecommerce'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT SELECT, INSERT, UPDATE ON ecommerce_agent.* TO 'ecommerce'@'localhost';
FLUSH PRIVILEGES;
```

---

## 故障排查

### 检查 MySQL 状态
```bash
sudo systemctl status mysqld
```

### 查看错误日志
```bash
sudo tail -f /var/log/mysqld.log
```

### 重启 MySQL
```bash
sudo systemctl restart mysqld
```

### 检查连接
```bash
mysql -u root -p'EcommerceAgent2026!' -e "SELECT 1"
```

---

**数据库状态**: ✅ 运行中  
**版本**: MySQL 8.0.44  
**数据**: 15 个商品已导入
