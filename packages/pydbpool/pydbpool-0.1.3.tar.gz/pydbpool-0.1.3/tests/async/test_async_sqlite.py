# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_async_sqlite.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import asyncio
import tempfile
import os

import pytest
import aiosqlite

from src.pydbpool.asyncdbpool import AsyncDBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError, PoolExhaustedError


@pytest.fixture(scope="module")
def event_loop():
    """创建事件循环fixture"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def async_sqlite_pool(event_loop):
    """创建异步SQLite连接池fixture"""
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
    pool = AsyncDBPool(
        connect_func=aiosqlite.connect,
        option=opt,
        database=db_path,
    )
    await pool.initialize()
    
    # 初始化测试表
    async with pool.connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)
        await conn.commit()
    
    yield pool
    await pool.close()
    
    # 清理临时文件
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.mark.asyncio
async def test_async_sqlite_basic_operations(async_sqlite_pool):
    """测试异步SQLite基本操作"""
    async with async_sqlite_pool.connection() as conn:
        # 插入数据
        await conn.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("async_test", 456))
        await conn.commit()
        
        # 查询数据
        cursor = await conn.execute("SELECT name, value FROM test_table WHERE name = ?", ("async_test",))
        result = await cursor.fetchone()
        
        assert result[0] == "async_test"
        assert result[1] == 456


@pytest.mark.asyncio
async def test_async_sqlite_concurrent_access(async_sqlite_pool):
    """测试异步SQLite并发访问"""
    async def worker(worker_id):
        try:
            async with async_sqlite_pool.connection() as conn:
                await conn.execute(
                    "INSERT INTO test_table (name, value) VALUES (?, ?)", 
                    (f"async_worker_{worker_id}", worker_id)
                )
                await conn.commit()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    tasks = []
    for i in range(5):
        tasks.append(worker(i))
    
    await asyncio.gather(*tasks)