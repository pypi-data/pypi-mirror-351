# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_async_postgresql.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import asyncio
import json
import random
import time

import pytest
import asyncpg

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
async def async_postgresql_pool(event_loop):
    """创建异步PostgreSQL连接池fixture"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,
    )
    pool = AsyncDBPool(
        connect_func=asyncpg.connect,
        option=opt,
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres",
    )
    await pool.initialize()
    yield pool
    await pool.close()


@pytest.mark.asyncio
async def test_async_postgresql_basic_operations(async_postgresql_pool):
    """测试异步PostgreSQL基本操作"""
    # 获取连接
    conn = await async_postgresql_pool.get_connection()
    
    # 执行查询
    result = await conn.fetchrow("SELECT 1 AS result")
    
    # 验证结果
    assert result[0] == 1
    
    # 释放连接
    await async_postgresql_pool.release_connection(conn)


@pytest.mark.asyncio
async def test_async_postgresql_context_manager(async_postgresql_pool):
    """测试异步PostgreSQL上下文管理器"""
    async with async_postgresql_pool.connection() as conn:
        result = await conn.fetchrow("SELECT 1+1 AS result")
        assert result[0] == 2


@pytest.mark.asyncio
async def test_async_postgresql_connection_reuse(async_postgresql_pool):
    """测试异步PostgreSQL连接复用"""
    # 记录初始连接池状态
    initial_total = async_postgresql_pool.meta.total_conn_count
    
    # 执行多次查询
    for _ in range(5):
        async with async_postgresql_pool.connection() as conn:
            await conn.fetchrow("SELECT 1")
    
    # 验证连接池没有无限增长
    assert async_postgresql_pool.meta.total_conn_count <= initial_total + async_postgresql_pool.opt.max_overflow


@pytest.mark.asyncio
async def test_async_postgresql_concurrent_access(async_postgresql_pool):
    """测试异步PostgreSQL并发访问"""
    async def worker():
        try:
            async with async_postgresql_pool.connection() as conn:
                # 使用pg_sleep函数模拟查询负载
                sleep_time = random.uniform(0.1, 0.5)
                await conn.fetchrow(f"SELECT pg_sleep({sleep_time})")
        except Exception as e:
            # 捕获可能的超时异常
            assert isinstance(e, (PoolTimeoutError, PoolExhaustedError))
    
    # 创建多个协程并发访问
    tasks = []
    for _ in range(10):  # 创建10个并发任务
        tasks.append(worker())
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_async_postgresql_connection_ping(async_postgresql_pool):
    """测试异步PostgreSQL连接健康检查"""
    conn = await async_postgresql_pool.get_connection()
    
    # 验证ping功能
    assert await conn.ping() is True
    
    await async_postgresql_pool.release_connection(conn)