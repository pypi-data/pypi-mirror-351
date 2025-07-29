# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : asyncdbpool.py
@Project  : 
@Time     : 2025/3/21 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import asyncio
import logging
from typing import Callable, Deque, Set, Type, AsyncContextManager
from collections import deque
from contextlib import asynccontextmanager

from .errors import PoolExhaustedError, PoolClosedError, PoolTimeoutError
from .base import BaseConnection, PoolOption, DBPoolMeta

logger = logging.getLogger("pydbpool")


class AsyncDBPoolConnection(BaseConnection):
    """异步数据库连接封装"""

    async def commit(self):
        return await self._conn.commit()

    async def rollback(self):
        return await self._conn.rollback()

    async def cursor(self):
        return await self._conn.cursor()

    @property
    def ping_query(self) -> str:
        conn_module = self._conn.__class__.__module__.lower()
        return "SELECT 1 FROM (SELECT 1) AS TEMP"  # noqa E501

    async def ping(self) -> bool:
        """异步执行探活检测"""
        with self._lock:
            try:
                # 优先使用原生ping方法
                if hasattr(self._conn, 'ping'):
                    try:
                        alive = await self._conn.ping()
                        if alive is None:
                            alive = True
                        return alive
                    except Exception:  # noqa S110
                        # 降级到查询检测
                        pass

                # 使用查询检测
                try:
                    cursor = await self._conn.cursor()
                    await cursor.execute(self.ping_query)
                    await cursor.fetchone()
                    await cursor.close()
                    return True
                except Exception as e:
                    logger.warning(f"Async ping query failed: {str(e)}")
                    return False

            except Exception as e:
                logger.warning(f"Async ping failed: {str(e)}")
                return False

    async def close(self) -> None:
        """安全关闭连接"""
        with self._lock:
            try:
                await self._conn.close()
                self.meta.update_close()
            except Exception:  # noqa S110
                pass


class AsyncDBPool:
    """异步数据库连接池实现"""

    def __init__(
            self,
            connect_func: Callable,
            connection_cls: Type[AsyncDBPoolConnection] = AsyncDBPoolConnection,
            option: PoolOption = PoolOption(pool_name="default_async_pool"),
            *args,
            **kwargs
    ):
        """初始化异步连接池"""
        self.connect_func = connect_func
        self.connection_cls = connection_cls
        self.opt = option
        self._args, self._kwargs = args, kwargs

        # 连接池状态
        self._idle_conns: Deque[AsyncDBPoolConnection] = deque()
        self._active_conns: Set[AsyncDBPoolConnection] = set()

        # 线程安全
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self._expand_attempts = 0
        self.meta = DBPoolMeta()

    async def _create_connection(self) -> AsyncDBPoolConnection:
        """创建新的异步连接"""
        conn, err = None, None
        for _ in range(self.opt.max_retries):
            try:
                raw_conn = await self.connect_func(*self._args, **self._kwargs)
                conn = self.connection_cls(raw_conn, self)
                break
            except Exception as e:
                await asyncio.sleep(0.5)
                err = e

        if err is not None:
            logger.error("异步连接创建失败", exc_info=err)
            raise PoolClosedError(f"异步连接创建失败: {err}") from err

        return conn

    def _collect_meta(self):
        self.meta.total_counter(len(self._idle_conns), len(self._active_conns))

    async def initialize(self):
        """初始化连接池"""
        async with self._lock:
            for _ in range(self.opt.minsize):
                self._idle_conns.append(await self._create_connection())
            self._collect_meta()

    async def get_connection(self) -> AsyncDBPoolConnection:
        """获取异步连接"""
        async with self._condition:
            if not self._idle_conns:
                # 检查是否达到最大连接数
                maxsize = self.opt.maxsize + self.opt.max_overflow
                current_size = len(self._idle_conns) + len(self._active_conns)
                if current_size >= maxsize:
                    raise PoolExhaustedError(
                        f"异步连接池已耗尽，达到最大连接数: {maxsize}，当前连接数: {current_size}"
                    )

                # 计算扩容数量
                expand_num = self._calculate_exponential_expand()
                logger.info("异步连接池无可用连接，进行扩容，当前扩容量：%s, 扩容指数：%s", expand_num,
                            self._expand_attempts)
                await self._expand_pool(expand_num)
                self._expand_attempts += 1
            else:
                self._expand_attempts = 0

            # 等待可用连接
            try:
                await asyncio.wait_for(
                    self._condition.wait_for(lambda: bool(self._idle_conns)),
                    timeout=self.opt.pool_timeout
                )
            except asyncio.TimeoutError:
                raise PoolTimeoutError(f"获取连接超时: {self.opt.pool_timeout}秒")

            conn = self._idle_conns.popleft()
            if self.opt.ping == 1:
                if not await conn.ping():
                    await conn.close()
                    conn = await self._create_connection()

            self._active_conns.add(conn)
            conn.meta.usage_counter()
            self.meta.borrow_counter(1)
            self._collect_meta()
            return conn

    async def release_connection(self, conn: AsyncDBPoolConnection) -> None:
        """归还异步连接"""
        async with self._condition:
            self._collect_meta()
            conn.meta.update_active_time()
            self.meta.borrow_counter(-1)

            try:
                self._active_conns.remove(conn)
            except KeyError:
                pass

            # 根据策略处理连接状态
            if self.opt.reset_on_return == 'rollback':
                await conn.rollback()
            elif self.opt.reset_on_return == 'commit':
                await conn.commit()

            # 检查连接健康状态
            if self.opt.ping == 2:
                if not await conn.ping():
                    await conn.close()
                    return

            # 检查连接是否需要回收
            if (
                    self.opt.max_usage and conn.meta.usage_count > self.opt.max_usage
            ) or (
                    self.opt.pool_recycle and conn.meta.lifetime > self.opt.pool_recycle
            ):
                await conn.close()
                return

            # 归还到空闲池
            self._idle_conns.append(conn)
            self._collect_meta()
            self._condition.notify()

    def _calculate_exponential_expand(self) -> int:
        """计算指数扩容数量"""
        max_allowed = self.opt.maxsize + self.opt.max_overflow
        remaining = max_allowed - len(self._idle_conns) - len(self._active_conns)
        base = 2 ** self._expand_attempts
        return min(base, remaining, self.opt.max_overflow)

    async def _expand_pool(self, n: int):
        """扩展连接池"""
        for _ in range(n):
            self._idle_conns.append(await self._create_connection())
        self._condition.notify_all()

    @asynccontextmanager
    async def connection(self) -> AsyncContextManager[AsyncDBPoolConnection]:
        """异步上下文管理器获取连接"""
        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await self.release_connection(conn)

    async def close(self):
        """关闭异步连接池"""
        async with self._condition:
            try:
                # 关闭所有空闲连接
                for conn in list(self._idle_conns):
                    await conn.close()
                self._idle_conns.clear()

                # 根据配置关闭活跃连接
                if self.opt.force_close:
                    for conn in list(self._active_conns):
                        await conn.close()
                    self._active_conns.clear()

                # 清理元数据
                self.meta.clear()
                self._condition.notify_all()
            except Exception as e:
                raise PoolClosedError(f"关闭异步连接池时出错: {e}") from e
