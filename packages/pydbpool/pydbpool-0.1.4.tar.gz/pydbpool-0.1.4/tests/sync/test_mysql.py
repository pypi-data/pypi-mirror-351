# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_mysql.py
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
import pymysql

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def mysql_pool():
    """创建MySQL连接池fixture"""
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
        port=3306,
        user="root",
        password="2012516nwdytL!",
        database="lamtun_dev",
    )
    yield pool
    pool.close()


def test_mysql_basic_operations(mysql_pool):
    """测试MySQL基本操作"""
    # 获取连接
    conn = mysql_pool.get_connection()
    
    # 创建游标并执行查询
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    # 验证结果
    assert result[0] == 1
    
    # 释放连接
    mysql_pool.release_connection(conn)


def test_mysql_context_manager(mysql_pool):
    """测试MySQL上下文管理器"""
    with mysql_pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1+1 AS result")
        result = cursor.fetchone()
        assert result[0] == 2


def test_mysql_connection_reuse(mysql_pool):
    """测试MySQL连接复用"""
    # 记录初始连接池状态
    initial_total = mysql_pool.meta.total_conn_count
    
    # 执行多次查询
    for _ in range(5):
        with mysql_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
    
    # 验证连接池没有无限增长
    assert mysql_pool.meta.total_conn_count <= initial_total + mysql_pool.opt.max_overflow


def test_mysql_concurrent_access(mysql_pool):
    """测试MySQL并发访问"""
    def worker():
        try:
            with mysql_pool.connection() as conn:
                cursor = conn.cursor()
                # 使用随机睡眠时间模拟查询负载
                sleep_time = random.uniform(0.1, 0.5)
                cursor.execute(f"SELECT SLEEP({sleep_time})")
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


def test_mysql_connection_ping(mysql_pool):
    """测试MySQL连接健康检查"""
    conn = mysql_pool.get_connection()
    
    # 验证ping功能
    assert conn.ping() is True
    
    mysql_pool.release_connection(conn)