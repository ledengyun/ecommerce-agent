#!/usr/bin/env python3
"""
测试 1688 浏览器访问
"""

import subprocess
import json
import time

def run_browser_cmd(action, *args, **kwargs):
    """执行 browser 命令"""
    cmd = ['openclaw', 'browser', action]
    
    for arg in args:
        if arg is not None:
            cmd.append(str(arg))
    
    for key, value in kwargs.items():
        if value is not None:
            flag = f'--{key.replace("_", "-")}'
            cmd.append(flag)
            if value is not True:
                cmd.append(str(value))
    
    print(f"执行：{' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
    
    if result.stdout:
        try:
            return json.loads(result.stdout)
        except:
            return {'output': result.stdout[:500]}
    
    if result.stderr:
        print(f"错误：{result.stderr}")
    
    return None

# 1. 打开 1688 移动端
print("="*60)
print("测试 1: 打开 1688 移动端首页")
print("="*60)

result = run_browser_cmd('open', 'https://m.1688.com')
print(f"结果：{json.dumps(result, indent=2, ensure_ascii=False)}")

target_id = result.get('targetId') if result else None

if target_id:
    # 2. 等待
    print("\n等待 5 秒...")
    time.sleep(5)
    
    # 3. 获取快照
    print("\n" + "="*60)
    print("测试 2: 获取页面快照")
    print("="*60)
    
    snapshot = run_browser_cmd('snapshot', format='ai', targetId=target_id)
    if snapshot:
        print(f"页面标题：{snapshot.get('title', 'N/A')}")
        print(f"页面文本预览：{str(snapshot.get('text', ''))[:500]}")
    
    # 4. 执行 JS 测试
    print("\n" + "="*60)
    print("测试 3: 执行 JavaScript 获取页面信息")
    print("="*60)
    
    js_test = """
    () => {
        return {
            url: window.location.href,
            title: document.title,
            bodyLength: document.body.innerHTML.length,
            hasProducts: document.querySelectorAll('.offer-item, .m-offer-item, .product-item').length > 0,
            userAgent: navigator.userAgent
        };
    }
    """
    
    js_result = run_browser_cmd('evaluate', fn=js_test, targetId=target_id)
    print(f"JS 执行结果：{json.dumps(js_result, indent=2, ensure_ascii=False)}")
    
    # 5. 关闭
    print("\n关闭浏览器...")
    run_browser_cmd('close', targetId=target_id)

print("\n✅ 测试完成")
