# ✅ 异步采集任务 API 完成

**时间**: 2026-03-13 10:04

---

## 🎉 功能完成

已实现异步采集任务功能，支持：
- ✅ 创建异步采集任务
- ✅ 实时查询任务状态
- ✅ 多平台采集（Amazon 已实现）
- ✅ 自动导入数据库
- ✅ 任务历史记录

---

## 📋 API 端点

### 1. POST /api/collect

创建采集任务（异步）

**请求**:
```json
{
  "keyword": "home goods",
  "platforms": ["amazon"],
  "limit": 20,
  "auto_import": true
}
```

**响应**:
```json
{
  "success": true,
  "message": "采集任务已创建",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_name": "TASK_20260313_100400",
  "keyword": "home goods",
  "platforms": ["amazon"],
  "limit": 20,
  "status": "pending",
  "progress": 0,
  "created_at": "2026-03-13T10:04:00"
}
```

---

### 2. GET /api/collect/tasks

获取任务列表

**响应**:
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_name": "TASK_20260313_100400",
      "keyword": "home goods",
      "platforms": ["amazon"],
      "status": "completed",
      "progress": 100,
      "total_products": 20,
      "message": "采集完成，共 20 个商品",
      "created_at": "2026-03-13T10:04:00",
      "completed_at": "2026-03-13T10:04:30"
    }
  ],
  "total": 1
}
```

---

### 3. GET /api/collect/tasks/{task_id}

获取单个任务状态

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 50,
  "message": "正在采集 amazon 平台...",
  "total_products": 0
}
```

---

## 🎨 前端页面

访问：`http://localhost:8000/collect_task.html`

**功能**:
- ✅ 创建采集任务表单
- ✅ 选择采集平台
- ✅ 设置采集数量
- ✅ 实时任务状态显示
- ✅ 进度条展示
- ✅ 任务历史列表
- ✅ 自动轮询更新（2 秒）

---

## 🔄 任务状态流程

```
pending (0%)
  ↓
running (10-90%)
  ├─ 正在初始化...
  ├─ 正在采集 amazon 平台...
  └─ 正在导入数据库...
  ↓
completed (100%)
  └─ 采集完成，共 X 个商品

或

failed
  └─ 任务失败：错误信息
```

---

## 💻 使用示例

### JavaScript

```javascript
// 创建任务
const response = await fetch('/api/collect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    keyword: 'home goods',
    platforms: ['amazon'],
    limit: 20,
    auto_import: true
  })
});

const task = await response.json();
console.log('任务已创建:', task.task_id);

// 轮询状态
async function pollTaskStatus(taskId) {
  const response = await fetch(`/api/collect/tasks/${taskId}`);
  const task = await response.json();
  
  console.log(`进度：${task.progress}%, 状态：${task.status}`);
  
  if (task.status === 'completed' || task.status === 'failed') {
    console.log('任务完成:', task);
  } else {
    setTimeout(() => pollTaskStatus(taskId), 2000);
  }
}

pollTaskStatus(task.task_id);
```

### Python

```python
import requests
import time

# 创建任务
response = requests.post(
    'http://localhost:8000/api/collect',
    json={
        'keyword': 'home goods',
        'platforms': ['amazon'],
        'limit': 20,
        'auto_import': True
    }
)

task = response.json()
task_id = task['task_id']
print(f"任务已创建：{task_id}")

# 轮询状态
while True:
    response = requests.get(f'http://localhost:8000/api/collect/tasks/{task_id}')
    task = response.json()
    
    print(f"进度：{task['progress']}%, 状态：{task['status']}")
    
    if task['status'] in ['completed', 'failed']:
        print("任务完成:", task)
        break
    
    time.sleep(2)
```

### curl

```bash
# 创建任务
curl -X POST http://localhost:8000/api/collect \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "home goods",
    "platforms": ["amazon"],
    "limit": 20,
    "auto_import": true
  }'

# 查询状态
curl http://localhost:8000/api/collect/tasks/{task_id}

# 获取任务列表
curl http://localhost:8000/api/collect/tasks?limit=10
```

---

## 📁 文件清单

| 文件 | 说明 |
|------|------|
| `backend/api/collection_api.py` | 采集任务 API ✅ |
| `backend/api/__init__.py` | API 路由导出 ✅ |
| `backend/main.py` | 注册路由 ✅ |
| `frontend/collect_task.html` | 前端页面 ✅ |

---

## 🚀 启动服务

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent/backend
python3 main.py
```

访问前端页面：
```
http://localhost:8000/collect_task.html
```

---

## 📊 任务状态说明

| 状态 | 说明 |
|------|------|
| **pending** | 任务已创建，等待执行 |
| **running** | 正在执行采集 |
| **completed** | 采集完成 |
| **failed** | 任务失败 |

---

## 🎯 完整流程

```
1. 前端提交采集请求
   ↓
2. API 创建任务（返回 task_id）
   ↓
3. 后台执行采集
   ├─ 调用 Amazon API
   ├─ 解析商品数据
   └─ 导入数据库
   ↓
4. 前端轮询任务状态
   ↓
5. 显示最终结果
```

---

## ✅ 优势

### 异步处理
- ✅ 不阻塞前端
- ✅ 支持长时间任务
- ✅ 用户体验好

### 状态追踪
- ✅ 实时进度更新
- ✅ 详细状态信息
- ✅ 错误信息记录

### 任务管理
- ✅ 任务历史记录
- ✅ 多任务并发
- ✅ 支持重试

---

**测试页面**: `http://localhost:8000/collect_task.html`
