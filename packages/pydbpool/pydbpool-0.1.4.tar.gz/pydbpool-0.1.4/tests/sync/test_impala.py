# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_impala.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import threading

import pytest
from impala.dbapi import connect

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def impala_pool():
    """创建Impala连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=10,
        pool_timeout=5,
    )
    pool = DBPool(
        connect_func=connect,
        option=opt,
        host="localhost",
        port=21050,
        database="default",
    )
    yield pool
    pool.close()


def test_impala_basic_operations(impala_pool):
    """测试Impala基本操作"""
    with impala_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_impala_show_tables(impala_pool):
    """测试Impala表操作"""
    with impala_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        assert isinstance(tables, list)


def test_impala_concurrent_access(impala_pool):
    """测试Impala并发访问"""
    def worker():
        try:
            with impala_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM (SELECT 1 AS col) t")
                cursor.fetchone()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    threads = []
    for _ in range(5):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()