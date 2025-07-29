# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_oracle.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import threading
import pytest
import oracledb

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def oracle_pool():
    """创建Oracle连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,
    )
    pool = DBPool(
        connect_func=oracledb.connect,
        option=opt,
        user="hr",
        password="oracle",
        dsn="localhost:1521/xe",
        encoding="UTF-8",
    )
    yield pool
    pool.close()


def test_oracle_basic_operations(oracle_pool):
    """测试Oracle基本操作"""
    with oracle_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        assert result[0] == 1


def test_oracle_context_manager(oracle_pool):
    """测试Oracle上下文管理器"""
    with oracle_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1+1 FROM DUAL")
        result = cursor.fetchone()
        assert result[0] == 2


def test_oracle_concurrent_access(oracle_pool):
    """测试Oracle并发访问"""

    def worker():
        try:
            with oracle_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DBMS_LOCK.SLEEP(0.1) FROM DUAL")
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


def test_oracle_connection_ping(oracle_pool):
    """测试Oracle连接健康检查"""
    conn = oracle_pool.get_connection()
    assert conn.ping() is True
    oracle_pool.release_connection(conn)
