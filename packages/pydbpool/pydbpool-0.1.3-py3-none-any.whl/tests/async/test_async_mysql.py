# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_async_mysql.py
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
async def async_mysql_pool(event_loop):
    """创建异步MySQL连接池fixture"""
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
        port=3306,
        user="root",
        password="2012516nwdytL!",
        database="lamtun_dev",
        loop=event_loop,
    )
    await pool.initialize()
    yield pool
    await pool.close()


@pytest.mark.asyncio
async def test_async_mysql_basic_operations(async_mysql_pool):
    """测试异步MySQL基本操作"""
    # 获取连接
    conn = await async_mysql_pool.get_connection()
    
    # 创建游标并执行查询
    cursor = await conn.cursor()
    await cursor.execute("SELECT 1")
    result = await cursor.fetchone()
    
    # 验证结果
    assert result[0] == 1
    
    # 释放连接
    await async_mysql_pool.release_connection(conn)


@pytest.mark.asyncio
async def test_async_mysql_context_manager(async_mysql_pool):
    """测试异步MySQL上下文管理器"""
    async with async_mysql_pool.connection() as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT 1+1 AS result")
        result = await cursor.fetchone()
        assert result[0] == 2


@pytest.mark.asyncio
async def test_async_mysql_connection_reuse(async_mysql_pool):
    """测试异步MySQL连接复用"""
    # 记录初始连接池状态
    initial_total = async_mysql_pool.meta.total_conn_count
    
    # 执行多次查询
    for _ in range(5):
        async with async_mysql_pool.connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1")
            await cursor.fetchone()
    
    # 验证连接池没有无限增长
    assert async_mysql_pool.meta.total_conn_count <= initial_total + async_mysql_pool.opt.max_overflow


@pytest.mark.asyncio
async def test_async_mysql_concurrent_access(async_mysql_pool):
    """测试异步MySQL并发访问"""
    async def worker():
        try:
            async with async_mysql_pool.connection() as conn:
                cursor = await conn.cursor()
                # 使用随机睡眠时间模拟查询负载
                sleep_time = random.uniform(0.1, 0.5)
                await cursor.execute(f"SELECT SLEEP({sleep_time})")
                await cursor.fetchone()
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
async def test_async_mysql_connection_ping(async_mysql_pool):
    """测试异步MySQL连接健康检查"""
    conn = await async_mysql_pool.get_connection()
    
    # 验证ping功能
    assert await conn.ping() is True
    
    await async_mysql_pool.release_connection(conn)