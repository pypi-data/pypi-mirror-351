# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_async_tidb.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import asyncio
import random

import pytest
import aiomysql

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
async def async_tidb_pool(event_loop):
    """创建异步TiDB连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,
    )
    pool = AsyncDBPool(
        connect_func=aiomysql.connect,
        option=opt,
        host="127.0.0.1",
        port=4000,
        user="root",
        password="",
        db="tests",
        charset="utf8mb4",
        loop=event_loop,
    )
    await pool.initialize()
    yield pool
    await pool.close()


@pytest.mark.asyncio
async def test_async_tidb_basic_operations(async_tidb_pool):
    """测试异步TiDB基本操作"""
    async with async_tidb_pool.connection() as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT 1")
        result = await cursor.fetchone()
        assert result[0] == 1


@pytest.mark.asyncio
async def test_async_tidb_distributed_features(async_tidb_pool):
    """测试异步TiDB分布式特性"""
    async with async_tidb_pool.connection() as conn:
        cursor = await conn.cursor()
        
        # 测试TiDB版本信息
        await cursor.execute("SELECT @@version_comment")
        version = await cursor.fetchone()
        assert "TiDB" in version[0]


@pytest.mark.asyncio
async def test_async_tidb_concurrent_access(async_tidb_pool):
    """测试异步TiDB并发访问"""
    async def worker():
        try:
            async with async_tidb_pool.connection() as conn:
                cursor = await conn.cursor()
                sleep_time = random.uniform(0.1, 0.5)
                await cursor.execute(f"SELECT SLEEP({sleep_time})")
                await cursor.fetchone()
        except Exception as e:
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    tasks = []
    for _ in range(10):
        tasks.append(worker())
    
    await asyncio.gather(*tasks)