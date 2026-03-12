// 1688 商品提取脚本 - 增强版（支持 100 个商品）
// 使用方法：
// 1. 在浏览器打开 1688 商品列表页/搜索页
// 2. 按 F12 打开开发者工具
// 3. 在 Console 中粘贴运行（输入 allow pasting）
// 4. 脚本会自动下载 JSON 文件（包含最多 100 个商品）

(() => {
    console.log('🔍 1688 商品提取 - 增强版（支持 100 个商品）\n');
    console.log('📍 当前页面:', window.location.href);
    console.log('📄 页面标题:', document.title);
    console.log('');
    
    // ========== 自动滚动页面加载更多商品 ==========
    console.log('📜 正在滚动页面加载更多商品...\n');
    
    const scrollSteps = 5;
    const scrollDelay = 800;
    
    for (let i = 0; i < scrollSteps; i++) {
        window.scrollTo(0, document.body.scrollHeight);
        // 等待
        const start = Date.now();
        while (Date.now() - start < scrollDelay) {
            // 等待加载
        }
    }
    
    // 滚动回顶部
    window.scrollTo(0, 0);
    
    console.log('✅ 页面滚动完成，开始提取商品...\n');
    
    const products = [];
    
    // ========== 智能查找子元素的函数 ==========
    function findElement(parent, selectors) {
        for (const sel of selectors) {
            const el = parent.querySelector(sel);
            if (el && el.textContent.trim()) {
                return el;
            }
        }
        return null;
    }
    
    function findPriceElement(parent) {
        const standard = findElement(parent, [
            '.price', '.current-price', '.sale-price',
            '.money', '.price-info', '[data-role="price"]',
            '.price-now', '[class*="price"]'
        ]);
        
        if (standard) return standard;
        
        const allTexts = parent.querySelectorAll('*');
        for (const el of allTexts) {
            const text = el.textContent.trim();
            if ((text.includes('¥') || text.includes('￥')) && text.length < 50) {
                return el;
            }
        }
        
        return null;
    }
    
    function findTitleElement(parent) {
        const standard = findElement(parent, [
            '.title', '.offer-title', '.product-title',
            'h2', 'h3', '.name', '.product-name',
            '[data-role="title"]', '[class*="title"]'
        ]);
        
        if (standard) return standard;
        
        let longestText = '';
        let longestEl = null;
        
        const allTexts = parent.querySelectorAll('*');
        for (const el of allTexts) {
            const text = el.textContent.trim();
            if (text.length > longestText.length && 
                text.length > 10 && 
                text.length < 200 &&
                !el.matches('button, script, style')) {
                longestText = text;
                longestEl = el;
            }
        }
        
        return longestEl;
    }
    
    // ========== 第一选择：标准选择器 ==========
    console.log('📋 尝试标准选择器...\n');
    
    const standardSelectors = [
        '.offer-item', '.m-offer-item', '.search-result-offer',
        '.item-mod', '.dp-offer-item', '.product-item',
        '[data-role="offer-item"]', '.list-item',
        '.wap-offer-item', '.mobile-offer', '.m-list-item'
    ];
    
    let items = [];
    let usedSelector = '';
    
    for (const selector of standardSelectors) {
        items = document.querySelectorAll(selector);
        if (items.length > 0) {
            console.log(`✅ 标准选择器：${selector} (${items.length} 个商品)`);
            usedSelector = selector;
            break;
        }
    }
    
    // ========== 第二选择：备用方案（价格匹配） ==========
    if (items.length === 0) {
        console.log('⚠️  标准选择器未找到，使用备用方案...\n');
        
        const allElements = document.querySelectorAll('div, li, article, section');
        
        items = Array.from(allElements).filter(el => {
            const text = el.textContent;
            const hasPrice = text.includes('¥') || text.includes('￥') || text.includes('$');
            const rightLength = text.length > 15 && text.length < 500;
            const notButton = !el.matches('button, input, a, nav, footer, header');
            const notChild = !el.parentElement?.closest('.offer-item, .m-offer-item, .product-item');
            
            return hasPrice && rightLength && notButton && notChild;
        });
        
        const uniqueItems = [];
        const seen = new Set();
        
        for (const item of items) {
            let isChild = false;
            for (const existing of uniqueItems) {
                if (existing.contains(item) || existing === item) {
                    isChild = true;
                    break;
                }
            }
            
            if (!isChild && !seen.has(item)) {
                seen.add(item);
                uniqueItems.push(item);
            }
        }
        
        items = uniqueItems.slice(0, 100);  // 支持 100 个商品
        
        if (items.length > 0) {
            console.log(`✅ 备用方案找到 ${items.length} 个商品元素（价格匹配）`);
            usedSelector = '备用方案（智能匹配）';
        }
    }
    
    // ========== 第三选择：广撒网 ==========
    if (items.length === 0) {
        console.log('⚠️  备用方案也未找到，使用广撒网方案...\n');
        
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const priceNodes = [];
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent;
            if ((text.includes('¥') || text.includes('￥')) && text.length > 5 && text.length < 100) {
                priceNodes.push(node.parentElement);
            }
        }
        
        items = [...new Set(priceNodes)].slice(0, 100);  // 支持 100 个商品
        
        if (items.length > 0) {
            console.log(`✅ 广撒网方案找到 ${items.length} 个商品元素`);
            usedSelector = '广撒网（文本节点）';
        }
    }
    
    // ========== 如果还是没找到 ==========
    if (items.length === 0) {
        console.log('❌ 未找到任何商品元素\n');
        console.log('可能的原因:');
        console.log('1. 页面还未完全加载（请向下滚动或等待）');
        console.log('2. 当前不是商品列表页（请在搜索结果页）');
        console.log('3. 需要登录才能查看（请先登录）');
        console.log('4. 网络问题导致页面未加载');
        console.log('\n建议:');
        console.log('- 向下滚动页面加载更多商品');
        console.log('- 刷新页面后重试');
        console.log('- 确认在搜索结果的列表页（不是首页）');
        console.log('- 登录 1688 账号后再试');
        return;
    }
    
    console.log(`\n📦 使用选择器：${usedSelector}`);
    console.log(`📦 准备提取 ${items.length} 个商品\n`);
    
    // ========== 提取商品信息 ==========
    items.forEach((item, index) => {
        try {
            const titleEl = findTitleElement(item);
            const title = titleEl?.textContent?.trim() || '';
            
            const priceEl = findPriceElement(item);
            const price = priceEl?.textContent?.trim() || '';
            
            const salesEl = findElement(item, [
                '.sales', '.sold', '.month-sales',
                '.deal-count', '.sold-count', '.repost-count',
                '[data-role="sales"]', '[class*="sales"]'
            ]);
            const sales = salesEl?.textContent?.trim() || '';
            
            const imageEl = item.querySelector('img');
            const image = imageEl?.src || imageEl?.dataset?.src || '';
            
            const linkEl = item.querySelector('a[href*="offer"]') || item.querySelector('a');
            const url = linkEl?.href || '';
            
            if (!title || title.length < 5) {
                console.log(`⚠️  跳过商品 ${index + 1}: 标题无效`);
                return;
            }
            
            const product = {
                index: index + 1,
                title: title,
                price: price || '价格未知',
                sales: sales || '',
                image: image,
                url: url,
                platform: '1688',
                extracted_at: new Date().toISOString()
            };
            
            products.push(product);
            
            const titlePreview = title.length > 50 ? title.substring(0, 50) + '...' : title;
            console.log(`✅ 商品 ${index + 1}: ${titlePreview} - ${price} ${sales ? '| ' + sales : ''}`);
            
        } catch (e) {
            console.error(`❌ 提取商品 ${index + 1} 失败:`, e.message);
        }
    });
    
    // ========== 输出结果 ==========
    console.log('\n' + '='.repeat(60));
    console.log(`✅ 成功提取 ${products.length} 个商品`);
    console.log('='.repeat(60));
    
    if (products.length > 0) {
        // 创建 JSON 数据
        const jsonData = {
            extracted_at: new Date().toISOString(),
            page_url: window.location.href,
            selector_used: usedSelector,
            total_products: products.length,
            products: products
        };
        
        const jsonString = JSON.stringify(jsonData, null, 2);
        
        // ========== 自动下载 JSON 文件 ==========
        console.log('\n💾 正在自动下载 JSON 文件...\n');
        
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `1688_products_${timestamp}.json`;
        
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`✅ 文件已下载：${filename}`);
        console.log(`📦 包含 ${products.length} 个商品`);
        console.log('\n📋 下一步操作:');
        console.log(`1. 将下载的文件重命名为：1688_products.json`);
        console.log(`2. 移动到项目目录：data/1688_products.json`);
        console.log(`3. 访问 Web 控制台：http://localhost:8000`);
        console.log(`4. 点击"开始分析"按钮`);
        
        // 同时也在控制台输出 JSON，方便手动复制
        console.log('\n' + '='.repeat(60));
        console.log('📋 JSON 数据（如需手动复制）:');
        console.log('='.repeat(60));
        console.log(jsonString);
        
    } else {
        console.log('\n⚠️  未提取到商品，请检查页面或重试');
    }
    
    return products;
})();
