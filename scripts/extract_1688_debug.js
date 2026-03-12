// 1688 商品提取脚本 - 增强调试版
// 使用方法：
// 1. 在浏览器打开 1688 商品列表页/搜索页
// 2. 按 F12 打开开发者工具
// 3. 在 Console 中粘贴运行（可能需要输入 allow pasting）
// 4. 复制输出的 JSON

(() => {
    console.log('🔍 1688 商品提取 - 增强版\n');
    console.log('📍 当前页面:', window.location.href);
    console.log('📄 页面标题:', document.title);
    console.log('');
    
    // ========== 第一步：扫描页面结构 ==========
    console.log('📊 页面结构扫描:\n');
    
    const stats = {
        totalDivs: document.querySelectorAll('div').length,
        totalLinks: document.querySelectorAll('a').length,
        totalImages: document.querySelectorAll('img').length,
        totalListItems: document.querySelectorAll('li').length,
        hasPrice: document.querySelectorAll('[class*="price"], [class*="money"]').length,
        hasOffer: document.querySelectorAll('[class*="offer"]').length,
        hasProduct: document.querySelectorAll('[class*="product"]').length,
        hasItem: document.querySelectorAll('[class*="item"]').length,
        hasList: document.querySelectorAll('[class*="list"], [role="list"]').length
    };
    
    console.log('页面元素统计:');
    console.table(stats);
    console.log('');
    
    // ========== 第二步：尝试找到商品容器 ==========
    console.log('🔎 查找商品元素...\n');
    
    // 扩展选择器列表
    const allSelectors = [
        // 常见商品选择器
        '.offer-item', '.m-offer-item', '.search-result-offer',
        '.item-mod', '.dp-offer-item', '.product-item',
        '[data-role="offer-item"]', '[data-role="product-item"]',
        
        // 列表项
        'li[role="listitem"]', 'li.list-item', '.list-content > div',
        
        // 通用选择器
        '.item', '.card', '.goods-item', '.product-card',
        
        // 移动端特定
        '.wap-offer-item', '.mobile-offer', '.m-list-item'
    ];
    
    let foundItems = [];
    let usedSelector = '';
    
    for (const selector of allSelectors) {
        const items = document.querySelectorAll(selector);
        if (items.length > 0) {
            console.log(`✅ 找到选择器: ${selector} (${items.length} 个)`);
            foundItems = Array.from(items);
            usedSelector = selector;
            break;
        }
    }
    
    // 如果还是没找到，尝试找包含价格的元素
    if (foundItems.length === 0) {
        console.log('⚠️  未找到标准商品元素，尝试备用方案...\n');
        
        const allDivs = document.querySelectorAll('div, li');
        foundItems = Array.from(allDivs).filter(el => {
            const text = el.textContent;
            // 查找包含价格符号且长度适中的元素
            return (text.includes('¥') || text.includes('￥') || text.includes('¥')) 
                && text.length > 10 
                && text.length < 300;
        }).slice(0, 20);
        
        if (foundItems.length > 0) {
            console.log(`✅ 备用方案找到 ${foundItems.length} 个包含价格的元素`);
            usedSelector = '备用方案（价格匹配）';
        }
    }
    
    if (foundItems.length === 0) {
        console.log('❌ 未找到任何商品元素');
        console.log('\n可能的原因:');
        console.log('1. 页面还未完全加载（请向下滚动或等待）');
        console.log('2. 当前不是商品列表页');
        console.log('3. 需要登录才能查看');
        console.log('4. 页面结构已变化');
        console.log('\n建议:');
        console.log('- 向下滚动页面加载更多商品');
        console.log('- 确认在搜索结果的列表页');
        console.log('- 刷新页面后重试');
        return;
    }
    
    console.log(`\n📦 使用选择器：${usedSelector}`);
    console.log(`📦 找到 ${foundItems.length} 个商品元素\n`);
    
    // ========== 第三步：提取商品信息 ==========
    console.log('📋 提取商品信息...\n');
    
    const products = [];
    
    // 智能查找子元素
    function findElement(parent, selectors) {
        for (const sel of selectors) {
            const el = parent.querySelector(sel);
            if (el && el.textContent.trim()) {
                return el;
            }
        }
        return null;
    }
    
    foundItems.forEach((item, index) => {
        try {
            // 查找各个字段
            const titleEl = findElement(item, [
                '.title', '.offer-title', '.product-title',
                'h2', 'h3', '.name', '.product-name',
                '[data-role="title"]', '[class*="title"]'
            ]);
            
            const priceEl = findElement(item, [
                '.price', '.current-price', '.sale-price',
                '.money', '.price-info', '[data-role="price"]',
                '.price-now', '[class*="price"]'
            ]);
            
            const salesEl = findElement(item, [
                '.sales', '.sold', '.month-sales',
                '.deal-count', '.sold-count', '.repost-count',
                '[data-role="sales"]', '[class*="sales"]'
            ]);
            
            const imageEl = item.querySelector('img');
            const linkEl = item.querySelector('a[href*="offer"]') || item.querySelector('a');
            
            const title = titleEl?.textContent?.trim() || '';
            const price = priceEl?.textContent?.trim() || '';
            
            // 只保存有标题的商品
            if (!title) {
                console.log(`⚠️  跳过商品 ${index + 1}: 无标题`);
                return;
            }
            
            products.push({
                index: index + 1,
                title: title,
                price: price || '价格未知',
                sales: salesEl?.textContent?.trim() || '',
                image: imageEl?.src || imageEl?.dataset?.src || '',
                url: linkEl?.href || '',
                platform: '1688',
                extracted_at: new Date().toISOString()
            });
            
            console.log(`✅ 商品 ${index + 1}: ${title.substring(0, 40)}... - ${price}`);
            
        } catch (e) {
            console.error(`❌ 提取商品 ${index + 1} 失败:`, e.message);
        }
    });
    
    // ========== 第四步：输出结果 ==========
    console.log('\n' + '='.repeat(60));
    console.log(`✅ 成功提取 ${products.length} 个商品`);
    console.log('='.repeat(60));
    
    if (products.length > 0) {
        console.log('\n📋 复制下方 JSON，保存为 data/1688_products.json:\n');
        console.log(JSON.stringify({
            extracted_at: new Date().toISOString(),
            page_url: window.location.href,
            selector_used: usedSelector,
            total_products: products.length,
            products: products
        }, null, 2));
    }
    
    return products;
})();
