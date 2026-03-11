// 1688 商品提取脚本 - 浏览器控制台版
// 使用方法：
// 1. 在浏览器打开 1688 商品列表页
// 2. 按 F12 打开开发者工具
// 3. 在 Console 中粘贴并运行此脚本
// 4. 复制输出的 JSON，保存为 data/1688_products.json

(() => {
    console.log('🔍 开始提取商品...\n');
    
    const products = [];
    
    // 尝试多种选择器
    const selectors = [
        '.offer-item',
        '.m-offer-item', 
        '.search-result-offer',
        '.item-mod',
        '.dp-offer-item',
        '[data-role="offer-item"]'
    ];
    
    let items = [];
    for (const selector of selectors) {
        items = document.querySelectorAll(selector);
        if (items.length > 0) {
            console.log(`✅ 找到选择器：${selector} (${items.length} 个商品)`);
            break;
        }
    }
    
    if (items.length === 0) {
        console.log('❌ 未找到商品元素');
        console.log('提示：请确保在商品列表页面');
        return;
    }
    
    items.forEach((item, index) => {
        try {
            const titleEl = item.querySelector('.title, .offer-title, .product-title, h2, h3, .name');
            const priceEl = item.querySelector('.price, .current-price, .sale-price, .money, .price-info');
            const salesEl = item.querySelector('.sales, .sold, .month-sales, .deal-count, .sold-count');
            const imageEl = item.querySelector('img');
            const linkEl = item.querySelector('a');
            
            const title = titleEl?.textContent?.trim() || '';
            
            if (!title) return; // 跳过无标题的
            
            products.push({
                index: index + 1,
                title: title,
                price: priceEl?.textContent?.trim() || '',
                sales: salesEl?.textContent?.trim() || '',
                image: imageEl?.src || '',
                url: linkEl?.href || '',
                platform: '1688',
                extracted_at: new Date().toISOString()
            });
        } catch (e) {
            console.error(`提取商品 ${index + 1} 失败:`, e);
        }
    });
    
    console.log(`\n✅ 成功提取 ${products.length} 个商品\n`);
    console.log('📋 复制下方 JSON，保存为 data/1688_products.json:\n');
    console.log(JSON.stringify({
        extracted_at: new Date().toISOString(),
        page_url: window.location.href,
        total_products: products.length,
        products: products
    }, null, 2));
    
    return products;
})();
