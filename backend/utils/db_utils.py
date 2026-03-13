#!/usr/bin/env python3
"""
数据库工具类
提供数据库连接、连接池管理等功能
"""

import logging
import pymysql
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from config import DB_CONFIG, DB_POOL_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._init_pool()
    
    def _init_pool(self):
        """初始化连接池"""
        try:
            # 简单连接池实现（生产环境建议使用 SQLAlchemy 或 aiomysql）
            self._pool = []
            for _ in range(DB_POOL_CONFIG['min_connections']):
                conn = self._create_connection()
                self._pool.append(conn)
            logger.info(f"数据库连接池初始化完成，大小：{len(self._pool)}")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败：{e}")
            raise
    
    def _create_connection(self):
        """创建数据库连接"""
        return pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=DB_POOL_CONFIG['connect_timeout']
        )
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            if self._pool:
                conn = self._pool.pop()
            else:
                conn = self._create_connection()
            
            yield conn
            
        except Exception as e:
            logger.error(f"数据库操作错误：{e}")
            raise
        finally:
            if conn:
                try:
                    if conn.open:
                        self._pool.append(conn)
                    else:
                        conn.close()
                except:
                    pass
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """执行 SQL（INSERT/UPDATE/DELETE）"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    result = cursor.execute(sql, params or ())
                conn.commit()
                return result
            except Exception as e:
                conn.rollback()
                logger.error(f"SQL 执行失败：{e}, SQL: {sql}")
                raise
    
    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params or ())
                    return cursor.fetchone()
            except Exception as e:
                logger.error(f"SQL 查询失败：{e}, SQL: {sql}")
                raise
    
    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """查询多条记录"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params or ())
                    return cursor.fetchall()
            except Exception as e:
                logger.error(f"SQL 查询失败：{e}, SQL: {sql}")
                raise
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """批量执行 SQL"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    result = cursor.executemany(sql, params_list)
                conn.commit()
                return result
            except Exception as e:
                conn.rollback()
                logger.error(f"批量 SQL 执行失败：{e}")
                raise
    
    def close(self):
        """关闭连接池"""
        if self._pool:
            for conn in self._pool:
                try:
                    if conn.open:
                        conn.close()
                except:
                    pass
            self._pool = None
            logger.info("数据库连接池已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 便捷函数
def get_db():
    """获取数据库管理器"""
    return db_manager


def execute_sql(sql: str, params: tuple = None):
    """执行 SQL"""
    return db_manager.execute(sql, params)


def query_one(sql: str, params: tuple = None):
    """查询单条"""
    return db_manager.fetch_one(sql, params)


def query_all(sql: str, params: tuple = None):
    """查询多条"""
    return db_manager.fetch_all(sql, params)
