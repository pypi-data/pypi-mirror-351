# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : errors.py
@Project  : 
@Time     : 2025/3/18 10:52
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""


class PoolBaseError(Exception):
    """Pool exception"""


class ConnectionBaseError(Exception):
    """Connection exception"""


class ConnectionTimeoutError(ConnectionBaseError):
    """Connection timeout exception"""


class ConnectionClosedError(ConnectionBaseError):
    """Connection closed exception"""


class ConnectionUnavailableError(ConnectionBaseError):
    """Connection unavailable exception"""


class ConnectionFailedError(ConnectionBaseError):
    """Connection failed exception"""


class ConnectionAttributeError(ConnectionBaseError):
    """Connection attribute exception"""


class PoolClosedError(PoolBaseError):
    """Pool closed exception"""


class PoolExhaustedError(PoolBaseError):
    """Pool exhausted exception"""


class PoolTimeoutError(PoolBaseError):
    """Pool timeout exception"""


class NotSupportModule(PoolBaseError):
    """Unsupported module"""


class ArgumentError(PoolBaseError):
    """Argument exception"""
