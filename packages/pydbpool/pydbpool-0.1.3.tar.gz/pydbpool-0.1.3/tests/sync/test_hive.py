# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_hive.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import threading

import pytest
from pyhive import hive

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def hive_pool():
    """创建Hive连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=2,  # Hive连接较重，减少最大连接数
        max_usage=1,
        max_retries=2,
        pool_recycle=30,  # Hive连接保持时间较长
        pool_timeout=10,  # Hive连接建立较慢
    )
    pool = DBPool(
        connect_func=hive.connect,
        option=opt,
        host="localhost",
        port=10000,
        username="hive",
        database="default",
    )
    yield pool
    pool.close()


def test_hive_basic_operations(hive_pool):
    """测试Hive基本操作"""
    with hive_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_hive_show_tables(hive_pool):
    """测试Hive表操作"""
    with hive_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        # 验证返回的是列表格式
        assert isinstance(tables, list)


def test_hive_concurrent_access(hive_pool):
    """测试Hive并发访问（较少并发数）"""
    def worker():
        try:
            with hive_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM (SELECT 1) t")
                cursor.fetchone()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    threads = []
    for _ in range(3):  # Hive并发数较少
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()