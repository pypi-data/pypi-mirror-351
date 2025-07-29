# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_sqlite.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import sqlite3
import threading
import tempfile
import os

import pytest

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def sqlite_pool():
    """创建SQLite连接池fixture"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=5,
        max_retries=2,
        pool_recycle=10,
        pool_timeout=3,
    )
    pool = DBPool(
        connect_func=sqlite3.connect,
        option=opt,
        database=db_path,
        check_same_thread=False,  # SQLite特有参数
    )
    
    # 初始化测试表
    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)
        conn.commit()
    
    yield pool
    pool.close()
    
    # 清理临时文件
    try:
        os.unlink(db_path)
    except OSError:
        pass


def test_sqlite_basic_operations(sqlite_pool):
    """测试SQLite基本操作"""
    with sqlite_pool.connection() as conn:
        cursor = conn.cursor()
        
        # 插入数据
        cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("tests", 123))
        conn.commit()
        
        # 查询数据
        cursor.execute("SELECT name, value FROM test_table WHERE name = ?", ("tests",))
        result = cursor.fetchone()
        
        assert result[0] == "tests"
        assert result[1] == 123


def test_sqlite_concurrent_access(sqlite_pool):
    """测试SQLite并发访问"""
    def worker(worker_id):
        try:
            with sqlite_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO test_table (name, value) VALUES (?, ?)", 
                    (f"worker_{worker_id}", worker_id)
                )
                conn.commit()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


def test_sqlite_connection_ping(sqlite_pool):
    """测试SQLite连接健康检查"""
    conn = sqlite_pool.get_connection()
    assert conn.ping() is True
    sqlite_pool.release_connection(conn)