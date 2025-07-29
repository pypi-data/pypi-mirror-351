# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbconnection.py
@Project  : 
@Time     : 2025/3/18 11:02
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from __future__ import annotations
import logging
from typing import Any, Optional

from .base import BaseConnection, DBConnMeta
from .errors import ConnectionAttributeError

logger = logging.getLogger("pydbpool")


class DBPoolConnection(BaseConnection):
    """稳定的数据库连接封装"""

    def __init__(
            self,
            raw_conn,
            pool: "DBPool",  # type: ignore
    ) -> None:
        """
        初始化稳定连接

        Args:
            raw_conn: 原始数据库连接对象
            pool: 连接池实例
        """
        super().__init__(raw_conn, pool)
        self.meta = DBConnMeta()

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def cursor(self):
        return self._conn.cursor()

    @property
    def ping_query(self) -> str:
        return "SELECT 1 FROM (SELECT 1) AS TEMP"  # noqa E501

    def ping(self) -> bool:
        """
        执行探活检测，支持多种数据库
        Returns:
            bool: 连接是否存活
        """
        with self._lock:
            try:
                # 优先使用原生ping方法
                if hasattr(self._conn, 'ping'):
                    try:
                        # MySQL风格ping
                        alive = self._conn.ping(False)
                        if alive is None:
                            alive = True
                        return alive
                    except TypeError:
                        try:
                            # 无参数ping
                            alive = self._conn.ping()
                            if alive is None:
                                alive = True
                            return alive
                        except Exception:  # noqa S110
                            # 降级到查询检测
                            pass
                
                # 使用查询检测
                try:
                    with self._conn.cursor() as cursor:
                        cursor.execute(self.ping_query)
                        cursor.fetchone()
                    return True
                except Exception as e:
                    logger.warning(f"Ping query failed: {str(e)}")
                    return False

            except Exception as e:
                logger.warning(f"Ping failed: {str(e)}")
                return False

    # @property
    # def ping_query(self) -> str:
    #     """根据不同数据库类型返回适合的ping查询"""
    #     # 检测数据库类型
    #     conn_module = self._conn.__class__.__module__.lower()
    #
    #     if 'sqlite' in conn_module:
    #         return "SELECT 1"
    #     elif 'mysql' in conn_module or 'pymysql' in conn_module:
    #         return "SELECT 1"
    #     elif 'postgresql' in conn_module or 'psycopg' in conn_module:
    #         return "SELECT 1"
    #     elif 'oracle' in conn_module or 'cx_oracle' in conn_module:
    #         return "SELECT 1 FROM DUAL"
    #     elif 'sqlserver' in conn_module or 'pyodbc' in conn_module or 'mssql' in conn_module:
    #         return "SELECT 1"
    #     else:
    #         # 通用查询，适用于大多数SQL数据库
    #         return "SELECT 1"
    #
    def close(self) -> None:
        """安全关闭连接"""
        with self._lock:
            try:
                self._conn.close()
                self.meta.update_close()
            except AttributeError:
                raise ConnectionAttributeError(f"Connection class ：{type(self._conn)} has no close-method")
            except Exception:  # noqa S110
                pass

    def __enter__(self) -> "DBPoolConnection":
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        self._pool.release_connection(self)  # 退出上下文时自动归还
