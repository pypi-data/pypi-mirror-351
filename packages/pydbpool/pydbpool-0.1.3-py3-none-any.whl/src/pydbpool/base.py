# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : base.py
@Project  : 
@Time     : 2025/3/18 10:57
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Dict, Any, Type, Callable, Literal, Union

from .dbapiinterface import Connection
from .errors import ArgumentError, ConnectionFailedError

logger = logging.getLogger("pydbpool")


@dataclass
class BaseMeta:
    created_at: float = time.monotonic()
    last_active: float = time.monotonic()
    is_closed: bool = False
    usage_count: int = 0
    lifetime: float = 0.0

    _lock = threading.Lock()

    def update_close(self):
        self.is_closed = True

    def usage_counter(self):
        with self._lock:
            self.usage_count += 1

    def update_active_time(self):
        with self._lock:
            self.last_active = time.monotonic()
            self.lifetime = self.last_active - self.created_at

    def clear(self) -> None:
        """清理元数据"""
        with self._lock:
            self.created_at: float = time.monotonic()
            self.last_active: float = time.monotonic()
            self.is_closed: bool = False
            self.usage_count: int = 0
            self.lifetime: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.__dict__


class DBConnMeta(BaseMeta):
    """连接元数据管理"""

    @property
    def avg_usage_feq(self) -> float:
        return self.lifetime / self.usage_count if self.usage_count > 0 else 0.0


class DBPoolMeta(BaseMeta):
    """连接池元数据"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_conn_count = 0
        self.using_conn_count = 0
        self.free_conn_count = 0

    def total_counter(self, free_cnt: int, using_cnt: int) -> None:
        """记录等待时间"""
        with self._lock:
            self.total_conn_count = free_cnt + using_cnt
            self.free_conn_count = free_cnt
            self.using_conn_count = using_cnt

    def borrow_counter(self, cnt: int) -> None:
        """记录使用时间"""
        with self._lock:
            self.using_conn_count += cnt
            self.free_conn_count = self.total_conn_count - self.using_conn_count

    def clear(self) -> None:
        """清理元数据"""
        super().clear()
        with self._lock:
            self.total_conn_count = 0
            self.using_conn_count = 0
            self.free_conn_count = 0


class BaseConnection(Connection, ABC):
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        self._conn_uid = uuid.uuid4().hex
        self._lock = threading.Lock()

    @abstractmethod
    def ping(self) -> bool:
        pass

    @property
    @abstractmethod
    def ping_query(self) -> str:
        pass

    @property
    def uuid(self):
        return self._conn_uid

    def __getattr__(self, item):
        try:
            # 直接访问实例属性
            return object.__getattribute__(self, item)
        except AttributeError:
            # 委托给原始连接
            return getattr(self._conn, item)


@dataclass
class PoolOption:
    """
    数据库连接池通用配置类
    参数按功能模块分组，兼容多连接池实现库
    """

    # --------------------------
    # 通用参数（跨库兼容）
    # --------------------------
    pool_name: str = "default_pool"
    """连接池唯一标识，用于日志或监控"""

    # blocking: bool = False
    # """当连接池资源耗尽时，是否阻塞等待可用连接"""

    # --------------------------
    # 连接生命周期控制
    # --------------------------
    max_overflow: int = 10
    """允许超过基础连接数的临时扩容数量，用于应对突发流量"""

    pool_recycle: Optional[int] = None
    """连接自动重建周期（秒），-1=永不回收，建议小于数据库的会话超时时间"""

    max_usage: int = 0
    """单个连接的最大复用次数，0=无限制，过高可能导致驱动级状态残留"""

    max_retries: int = 3
    """连接创建失败时的最大重试次数，网络不稳定时建议调高"""

    idle_timeout: Optional[int] = None
    """空闲连接自动关闭的超时时间（秒），None=不启用"""

    # --------------------------
    # 连接池容量配置
    # --------------------------
    minsize: int = 1
    """连接池保持的最小空闲连接数，冷启动时预初始化"""

    maxsize: Optional[Union[int, float]] = 3
    """连接池允许的最大连接数，生产环境建议设置上限, None 则无限制"""

    # --------------------------
    # 连接状态管理
    # --------------------------
    reset_on_return: Literal[None, 'commit', 'rollback'] = 'rollback'
    """归还连接时的默认事务处理策略：提交/回滚/不操作"""

    ping: int = 1
    """连接健康检查策略：0=禁用，1=从链接池获取时检查，2=放回池前检查"""

    pool_timeout: Optional[float] = None
    """从连接池获取连接的最大等待时间（秒）, None 则一直等待直到获取成功"""

    force_close: bool = False
    """关闭连接池时，是否关闭活跃的数据库连接"""

    def __post_init__(self):
        """参数校验入口，按功能模块分组校验"""
        self._assert_connection_limits()
        self._assert_lifecycle()
        self._assert_state_policies()

    # --------------------------
    # 校验方法（内部实现）
    # --------------------------
    def _assert_connection_limits(self):
        """连接数相关参数校验"""
        if not isinstance(self.max_overflow, int) or self.max_overflow < -1:
            raise ArgumentError("连接扩容数必须为-1或非负整数")

        if not isinstance(self.minsize, int):
            raise ArgumentError("最小连接数必须为整数")
            
        if self.minsize < 0:
            raise ArgumentError("最小连接数不能为小于0的数")

        if not self.maxsize:
            self.maxsize = float('inf')
        elif not isinstance(self.maxsize, (int, float)):
            raise ArgumentError("最大连接数必须为数字")

        if self.maxsize < 0:
            raise ArgumentError("最大连接数不能为负数")

        if 0 < self.maxsize < self.minsize:
            raise ArgumentError("最小连接数不能超过最大连接数")
            
    def _assert_lifecycle(self):
        """连接生命周期参数校验"""
        if not isinstance(self.pool_recycle, (int, type(None))):
            raise ArgumentError("连接回收周期必须为None 或 正整数")

        if not isinstance(self.max_usage, int) or self.max_usage < 0:
            raise ArgumentError("最大复用次数不能为负数")

        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            raise ArgumentError("最大重试次数不能为负数")

        if self.idle_timeout is not None and self.idle_timeout < 0:
            raise ArgumentError("空闲超时时间不能为负数")

    def _assert_state_policies(self):
        """连接状态策略校验"""
        valid_reset = (None, 'commit', 'rollback')
        if self.reset_on_return not in valid_reset:
            raise ArgumentError(f"连接重置策略必须是 {valid_reset} 之一")

        if self.ping not in (0, 1, 2):
            raise ArgumentError("健康检查策略代码必须是0、1或2")

        if self.pool_timeout and self.pool_timeout <= 0:
            raise ArgumentError("连接等待超时必须大于0秒")


class BasePool(ABC):

    def __init__(self,
                 connect_func: Union[Type[Connection], Callable],
                 connect_cls: Type[BaseConnection],
                 option: PoolOption,
                 *args, **kwargs
                 ):
        self.connect_func = connect_func
        self.connect_cls = connect_cls
        self.opt = option
        self._args, self._kwargs = args, kwargs

    def _create_connection(self) -> "BaseConnection":
        conn, err = None, None
        for _ in range(self.opt.max_retries):
            try:
                conn = self.connect_cls(self.connect_func(*self._args, **self._kwargs), self)
                break
            except Exception as e:  # noqa S110
                time.sleep(.5)
                err = e

        if err is not None:
            logger.error("连接创建失败", exc_info=err)
            raise ConnectionFailedError(f"连接创建失败: {err}") from err

        return conn

    @abstractmethod
    def get_connection(self) -> BaseConnection:
        pass

    @abstractmethod
    @contextmanager
    def connection(self) -> BaseConnection:
        pass

    @abstractmethod
    def release_connection(self, conn: BaseConnection) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def update_pool(self, opt: PoolOption):
        pass

    @abstractmethod
    def close_connection(self, conn_uuid: str):
        pass
