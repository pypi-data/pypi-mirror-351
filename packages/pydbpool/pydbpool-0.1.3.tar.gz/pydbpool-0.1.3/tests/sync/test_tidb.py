# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_tidb.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import threading
import random

import pytest
import pymysql

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def tidb_pool():
    """创建TiDB连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,
    )
    pool = DBPool(
        connect_func=pymysql.connect,
        option=opt,
        host="127.0.0.1",
        port=4000,  # TiDB默认端口
        user="root",
        password="",
        database="tests",
        charset="utf8mb4",
    )
    yield pool
    pool.close()


def test_tidb_basic_operations(tidb_pool):
    """测试TiDB基本操作"""
    with tidb_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_tidb_distributed_features(tidb_pool):
    """测试TiDB分布式特性"""
    with tidb_pool.connection() as conn:
        cursor = conn.cursor()
        
        # 测试TiDB版本信息
        cursor.execute("SELECT @@version_comment")
        version = cursor.fetchone()[0]
        assert "TiDB" in version
        
        # 测试TiDB特有的系统表
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.CLUSTER_INFO")
        result = cursor.fetchone()
        assert result[0] >= 0


def test_tidb_concurrent_access(tidb_pool):
    """测试TiDB并发访问"""
    def worker():
        try:
            with tidb_pool.connection() as conn:
                cursor = conn.cursor()
                sleep_time = random.uniform(0.1, 0.5)
                cursor.execute(f"SELECT SLEEP({sleep_time})")
                cursor.fetchone()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()