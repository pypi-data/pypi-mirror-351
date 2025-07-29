# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_postgresql.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
import random
import threading
import time

import pytest
import psycopg2

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def postgresql_pool():
    """创建PostgreSQL连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,
    )
    pool = DBPool(
        connect_func=psycopg2.connect,
        option=opt,
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres",
    )
    yield pool
    pool.close()


def test_postgresql_basic_operations(postgresql_pool):
    """测试PostgreSQL基本操作"""
    # 获取连接
    conn = postgresql_pool.get_connection()
    
    # 创建游标并执行查询
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    # 验证结果
    assert result[0] == 1
    
    # 释放连接
    postgresql_pool.release_connection(conn)


def test_postgresql_context_manager(postgresql_pool):
    """测试PostgreSQL上下文管理器"""
    with postgresql_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1+1 AS result")
        result = cursor.fetchone()
        assert result[0] == 2


def test_postgresql_connection_reuse(postgresql_pool):
    """测试PostgreSQL连接复用"""
    # 记录初始连接池状态
    initial_total = postgresql_pool.meta.total_conn_count
    
    # 执行多次查询
    for _ in range(5):
        with postgresql_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
    
    # 验证连接池没有无限增长
    assert postgresql_pool.meta.total_conn_count <= initial_total + postgresql_pool.opt.max_overflow


def test_postgresql_concurrent_access(postgresql_pool):
    """测试PostgreSQL并发访问"""
    def worker():
        try:
            with postgresql_pool.connection() as conn:
                cursor = conn.cursor()
                # 使用pg_sleep函数模拟查询负载
                sleep_time = random.uniform(0.1, 0.5)
                cursor.execute(f"SELECT pg_sleep({sleep_time})")
                cursor.fetchone()
        except Exception as e:
            # 捕获可能的超时异常
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    # 创建多个线程并发访问
    threads = []
    for _ in range(10):  # 创建10个并发线程
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()


def test_postgresql_connection_ping(postgresql_pool):
    """测试PostgreSQL连接健康检查"""
    conn = postgresql_pool.get_connection()
    
    # 验证ping功能
    assert conn.ping() is True
    
    postgresql_pool.release_connection(conn)