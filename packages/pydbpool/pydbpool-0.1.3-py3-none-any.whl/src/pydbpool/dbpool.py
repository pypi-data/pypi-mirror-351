# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbpool.py
@Project  : 
@Time     : 2025/3/18 11:03
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import threading
import logging
from typing import Any, Callable, Deque, Set, Type
from collections import deque
from contextlib import contextmanager

from .errors import PoolExhaustedError, PoolClosedError, PoolTimeoutError
from .base import BaseConnection, BasePool, PoolOption, DBPoolMeta
from .dbconnection import DBPoolConnection

logger = logging.getLogger("pydbpool")


class DBPool(BasePool):

    def __init__(self,
                 connect_func: Callable,
                 connection_cls: Type[BaseConnection] = DBPoolConnection,
                 option: PoolOption = PoolOption(pool_name="default_pool"),
                 *args,
                 **kwargs
                 ):
        """
        初始化连接池

        Args:
            connect_func: 创建数据库连接的函数， eg. pymysql.connect
            connection_cls: 连接类，默认为DBPoolConnection,可以自定义继承自BaseConnection实现自己的连接类
            minsize: 最小连接数，默认为1
            maxsize: 最大连接数，默认为2
            max_retries: 连接失败最大重试次数，默认为3
            max_usage: 单个连接最大使用次数，默认为None（无限制）
            ping_query: 探活查询语句，默认为None
            idle_timeout: 空闲连接超时时间（秒），默认为None（无限制）
            wait_timeout: 获取连接等待超时时间（秒），默认为None（无限制）
            auto_increase: 是否允许自动增加连接，默认为True
            health_check_interval: 健康检查间隔（秒），默认为3600

            *args, **kwargs: 全部传递给connect_func
        """
        super().__init__(connect_func, connection_cls, option, *args, **kwargs)

        # 连接池状态
        self._idle_conns: Deque[DBPoolConnection | connection_cls] = deque()
        self._active_conns: Set[DBPoolConnection | connection_cls] = set()

        # 线程安全
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._expand_attempts = 0  # 连续扩容尝试次数
        self.meta = DBPoolMeta()

        # 初始化连接池
        for _ in range(self.opt.minsize):
            self._idle_conns.append(self._create_connection())
        self._collect_meta()

    def _collect_meta(self):
        self.meta.total_counter(len(self._idle_conns), len(self._active_conns))

    def release_connection(self, conn: DBPoolConnection) -> None:
        with self._cond:
            self._collect_meta()
            conn.meta.update_active_time()
            self.meta.borrow_counter(-1)
            try:
                self._active_conns.remove(conn)
            except IndexError:
                pass

            if self.opt.reset_on_return == 'rollback':
                conn.rollback()
            elif self.opt.reset_on_return == 'commit':
                conn.commit()

            # 根据连接池配置检测
            if self.opt.ping == 2:
                if not conn.ping():
                    conn.close()
                    return

            if (
                    self.opt.max_usage
                    and conn.meta.usage_count > self.opt.max_usage
            ) or (
                    self.opt.pool_recycle
                    and conn.meta.lifetime > self.opt.pool_recycle
            ):
                conn.close()
                return

            self._idle_conns.append(conn)
            self._collect_meta()
            self._cond.notify()

    def get_connection(self) -> DBPoolConnection | Any:
        """获取连接（带精确超时控制）"""

        with self._cond:
            if not self._idle_conns:
                # 连接池没有上限
                maxsize = self.opt.maxsize + self.opt.max_overflow
                current_size = len(self._idle_conns) + len(self._active_conns)
                if current_size > maxsize:
                    raise PoolExhaustedError(
                        f"Pool is exhausted and reached maxsize ：{maxsize}， current size is:{current_size}")

                expand_num = self._calculate_exponential_expand()
                logger.info("连接池无可用连接，进行扩容，当前扩容量：%s, 扩容指数：%s", expand_num, self._expand_attempts)
                self._expand_pool(expand_num)
                self._expand_attempts += 1  # 递增尝试次数
            else:
                self._expand_attempts = 0  # 重置计数器

            # 扩容后还是没有可用连接即等待指定时间
            if not self._cond.wait_for(
                    lambda: bool(self._idle_conns),
                    timeout=self.opt.pool_timeout
            ):
                raise PoolTimeoutError(f"exceed time limit: {self.opt.pool_timeout}, when getting an idle connection.")

            conn = self._idle_conns.popleft()
            if self.opt.ping == 1:
                if not conn.ping():
                    conn.close()
                    conn = self._create_connection()

            self._active_conns.add(conn)

            conn.meta.usage_counter()
            self.meta.borrow_counter(1)
            self._collect_meta()
            return conn

    def _calculate_exponential_expand(self) -> int:
        """指数级增量计算"""
        # 计算剩余可扩容空间
        max_allowed = self.opt.maxsize + self.opt.max_overflow
        remaining = max_allowed - len(self._idle_conns) - len(self._active_conns)

        # 基础增量 = 2^尝试次数
        base = 2 ** self._expand_attempts

        # 最终增量 = min(基础增量, 剩余空间, max_overflow)
        return min(base, remaining, self.opt.max_overflow)

    def _expand_pool(self, n: int):
        for _ in range(n):
            self._idle_conns.append(self._create_connection())
        self._cond.notify_all()

    def update_pool(self, opt: PoolOption):
        """更新连接池配置
        
        Args:
            opt: 新的连接池配置选项
        """
        with self._cond:
            # 验证新配置的有效性
            old_opt = self.opt
            self.opt = opt
            
            # 如果最小连接数增加，则创建新连接
            if opt.minsize > old_opt.minsize:
                for _ in range(opt.minsize - old_opt.minsize):
                    self._idle_conns.append(self._create_connection())
            
            # 如果最大连接数减少，可能需要关闭一些空闲连接
            if opt.maxsize < old_opt.maxsize and len(self._idle_conns) > opt.minsize:
                # 保留最小连接数，关闭多余的
                to_close = len(self._idle_conns) - opt.minsize
                for _ in range(to_close):
                    conn = self._idle_conns.pop()  # 移除最后添加的连接
                    conn.close()
            
            # 更新元数据
            self._collect_meta()
            logger.info(f"连接池 {self.opt.pool_name} 配置已更新: {old_opt} -> {opt}")

    def close_connection(self, conn_uuid: str):
        """关闭指定连接"""
        con = None
        for conn in self._idle_conns:
            if conn.uuid == conn_uuid:
                con = conn
                break

        if con is not None:
            con.close()
            self._idle_conns.remove(con)

    @contextmanager
    def connection(self) -> DBPoolConnection:
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.release_connection(conn)

    def close(self):
        """关闭所有连接"""
        with self._cond:
            try:
                # 关闭所有空闲连接
                for conn in list(self._idle_conns):
                    conn.close()

                self._idle_conns.clear()

                if self.opt.force_close:
                    conn.close()
                    self._active_conns.clear()

                # 清理元数据
                self.meta.clear()

                # 通知所有等待线程
                self._cond.notify_all()
            except Exception as e:
                raise PoolClosedError(f"Error during pool closure: {e}") from e
