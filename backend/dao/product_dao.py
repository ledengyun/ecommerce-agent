#!/usr/bin/env python3
"""
产品数据访问对象
负责产品的数据库操作
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from utils.db_utils import get_db

logger = logging.getLogger(__name__)


class ProductDAO:
    """产品数据访问对象"""
    
    def __init__(self):
        self.db = get_db()
    
    def insert_product(self, product: Dict[str, Any]) -> int:
        """
        插入单个商品
        
        Args:
            product: 商品数据
            
        Returns:
            插入的商品 ID
        """
        sql = """
        INSERT INTO products 
        (title, price, supplier_price, retail_price, profit_margin,
         image_url, source_url, sales, rating, recommend, platform)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            product.get('title', '未知商品'),
            product.get('price'),
            product.get('supplier_price'),
            product.get('retail_price'),
            product.get('profit_margin'),
            product.get('image_url'),
            product.get('source_url'),
            product.get('sales'),
            product.get('rating'),
            product.get('recommend', False),
            product.get('platform', 'unknown')
        )
        
        return self.db.execute(sql, params)
    
    def insert_products_batch(self, products: List[Dict[str, Any]]) -> int:
        """
        批量插入商品
        
        Args:
            products: 商品列表
            
        Returns:
            插入的商品数量
        """
        sql = """
        INSERT INTO products 
        (title, price, supplier_price, retail_price, profit_margin,
         image_url, source_url, sales, rating, recommend, platform)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params_list = []
        for p in products:
            params = (
                p.get('title', '未知商品'),
                p.get('price'),
                p.get('supplier_price'),
                p.get('retail_price'),
                p.get('profit_margin'),
                p.get('image_url'),
                p.get('source_url'),
                p.get('sales'),
                p.get('rating'),
                p.get('recommend', False),
                p.get('platform', 'unknown')
            )
            params_list.append(params)
        
        return self.db.execute_many(sql, params_list)
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 查询商品"""
        sql = "SELECT * FROM products WHERE id = %s"
        return self.db.fetch_one(sql, (product_id,))
    
    def get_products(
        self,
        limit: int = 50,
        offset: int = 0,
        platform: str = None,
        recommend: bool = None
    ) -> List[Dict[str, Any]]:
        """
        查询商品列表
        
        Args:
            limit: 返回数量
            offset: 偏移量
            platform: 平台过滤
            recommend: 是否推荐过滤
            
        Returns:
            商品列表
        """
        conditions = []
        params = []
        
        if platform:
            conditions.append("platform = %s")
            params.append(platform)
        
        if recommend is not None:
            conditions.append("recommend = %s")
            params.append(recommend)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        sql = f"""
        SELECT * FROM products 
        {where_clause}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        return self.db.fetch_all(sql, tuple(params))
    
    def get_unanalyzed_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取未分析的商品"""
        sql = """
        SELECT id, title, supplier_price, sales_volume, image_url, source_url
        FROM products 
        WHERE analyzed = FALSE OR analyzed IS NULL
        ORDER BY id DESC
        LIMIT %s
        """
        return self.db.fetch_all(sql, (limit,))
    
    def get_analyzed_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取已分析的商品"""
        sql = """
        SELECT id, title, supplier_price, retail_price, profit_margin,
               image_url, source_url, recommend, last_analyzed_at
        FROM products 
        WHERE analyzed = TRUE
        ORDER BY profit_margin DESC
        LIMIT %s
        """
        return self.db.fetch_all(sql, (limit,))
    
    def update_product(self, product_id: int, data: Dict[str, Any]) -> int:
        """
        更新商品
        
        Args:
            product_id: 商品 ID
            data: 要更新的数据
            
        Returns:
            影响的行数
        """
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        params = list(data.values()) + [product_id]
        
        sql = f"""
        UPDATE products 
        SET {set_clause}
        WHERE id = %s
        """
        
        return self.db.execute(sql, tuple(params))
    
    def delete_product(self, product_id: int) -> int:
        """删除商品"""
        sql = "DELETE FROM products WHERE id = %s"
        return self.db.execute(sql, (product_id,))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        sql = """
        SELECT 
            COUNT(*) as total_products,
            SUM(CASE WHEN analyzed = TRUE THEN 1 ELSE 0 END) as analyzed_count,
            SUM(CASE WHEN analyzed = FALSE THEN 1 ELSE 0 END) as unanalyzed_count,
            SUM(CASE WHEN recommend = TRUE THEN 1 ELSE 0 END) as recommended_count,
            AVG(CASE WHEN analyzed = TRUE THEN profit_margin ELSE NULL END) as avg_profit_margin
        FROM products
        """
        return self.db.fetch_one(sql)
    
    def get_platform_stats(self) -> List[Dict[str, Any]]:
        """获取各平台统计"""
        sql = """
        SELECT 
            platform,
            COUNT(*) as total,
            AVG(profit_margin) as avg_margin,
            SUM(CASE WHEN recommend = TRUE THEN 1 ELSE 0 END) as recommended
        FROM products
        GROUP BY platform
        """
        return self.db.fetch_all(sql)


# 全局 DAO 实例
product_dao = ProductDAO()


# 便捷函数
def get_product_dao():
    """获取 ProductDAO 实例"""
    return product_dao
