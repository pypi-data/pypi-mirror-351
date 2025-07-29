# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_doris.py
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
def doris_pool():
    """创建Doris连接池fixture"""
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
        port=9030,  # Doris查询端口
        user="root",
        password="",
        database="demo",
        charset="utf8mb4",
    )
    yield pool
    pool.close()


def test_doris_basic_operations(doris_pool):
    """测试Doris基本操作"""
    with doris_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_doris_show_backends(doris_pool):
    """测试Doris集群信息"""
    with doris_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW BACKENDS")
        backends = cursor.fetchall()
        assert isinstance(backends, (list, tuple))


def test_doris_concurrent_access(doris_pool):
    """测试Doris并发访问"""
    def worker():
        try:
            with doris_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SLEEP(0.1)")
                cursor.fetchone()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    threads = []
    for _ in range(8):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()