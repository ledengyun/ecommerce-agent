#!/usr/bin/env python3
"""
调试 1688 页面结构
"""

import subprocess
import json
import time
import re

def run_browser_cmd(action, **kwargs):
    cmd = ['openclaw', 'browser', action]
    for key, value in kwargs.items():
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
            return {'output': result.stdout}
    return None

# 打开 1688 搜索页
print("打开 1688 搜索：跨境专供")
result = run_browser_cmd('open', url='https://m.1688.com/page/search.html?keywords=跨境专供')
print(f"打开结果：{result}")

# 提取 targetId
target_id = None
if result and 'output' in result:
    match = re.search(r'id: ([A-F0-9]+)', result['output'])
    if match:
        target_id = match.group(1)
        print(f"Target ID: {target_id}")

if target_id:
    print("\n等待 8 秒让页面加载...")
    time.sleep(8)
    
    # 获取快照
    print("\n获取页面快照...")
    snapshot = run_browser_cmd('snapshot', format='ai', **{'target-id': target_id})
    
    if snapshot:
        print(f"\n页面标题：{snapshot.get('title', 'N/A')}")
        print(f"\n页面文本 (前 1000 字符):")
        print(str(snapshot.get('text', ''))[:1000])
        
        # 检查是否触发反爬
        text = str(snapshot.get('text', ''))
        if 'unusual traffic' in text.lower() or '检测' in text or '安全验证' in text:
            print("\n⚠️  检测到反爬页面！")
        else:
            print("\n✅ 页面正常加载")
    
    # 执行 JS 查看页面结构
    print("\n\n执行 JS 查看页面结构...")
    js_check = """
    () => {
        const info = {
            url: window.location.href,
            title: document.title,
            bodyLength: document.body.innerHTML.length,
            allLinks: document.querySelectorAll('a').length,
            allImages: document.querySelectorAll('img').length,
            // 尝试各种可能的商品选择器
            selectors: {
                'offer-item': document.querySelectorAll('.offer-item').length,
                'm-offer-item': document.querySelectorAll('.m-offer-item').length,
                'product-item': document.querySelectorAll('.product-item').length,
                'list-item': document.querySelectorAll('.list-item').length,
                'item': document.querySelectorAll('.item').length,
            }
        };
        
        // 找价格元素
        const priceEls = document.querySelectorAll('[class*="price"], [class*="money"]');
        info.priceCount = priceEls.length;
        if (priceEls.length > 0) {
            info.samplePrices = Array.from(priceEls).slice(0, 3).map(el => el.textContent.trim());
        }
        
        // 找标题元素
        const titleEls = document.querySelectorAll('[class*="title"], h2, h3');
        info.titleCount = titleEls.length;
        
        return info;
    }
    """
    
    js_result = run_browser_cmd('evaluate', fn=js_check, **{'target-id': target_id})
    print(f"JS 结果：{json.dumps(js_result, indent=2, ensure_ascii=False)}")
    
    # 关闭
    print("\n关闭浏览器...")
    run_browser_cmd('close', **{'target-id': target_id})

print("\n✅ 调试完成")
