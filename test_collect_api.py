#!/usr/bin/env python3
"""
测试数据采集 API
"""

import requests
import json

# 测试采集 API
response = requests.post(
    'http://localhost:8000/api/collect',
    json={
        'keyword': 'home goods',
        'platforms': ['1688'],
        'limit': 10
    }
)

print(f"状态码：{response.status_code}")
print(f"\n响应结果:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
