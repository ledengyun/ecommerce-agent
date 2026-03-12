#!/usr/bin/env python3
"""
简单的图片代理 - 解决 1688 图片防盗链问题
"""

import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/proxy')
def proxy_image():
    image_url = request.args.get('url', '')
    
    if not image_url:
        return Response("Missing URL parameter", status=400)
    
    try:
        # 添加 Referer 头绕过防盗链
        headers = {
            'Referer': 'https://www.1688.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        
        # 返回图片
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'image/webp')
        )
        
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
