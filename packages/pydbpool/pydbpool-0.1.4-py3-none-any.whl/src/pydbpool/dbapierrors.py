# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbapierrors.py
@Project  : 
@Time     : 2025/3/19 21:10
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""


class Warning_(Exception):
    """ 非致命警告的基类 """
    pass


class Error(Exception):
    """ 所有错误异常的基类 """
    pass


# Error 的直接子类
class InterfaceError(Error):
    """ 接口相关错误（如无效参数） """
    pass


class DatabaseError(Error):
    """ 数据库操作相关错误的基类 """
    pass


# DatabaseError 的子类
class DataError(DatabaseError):
    """ 数据处理错误（如数值越界） """
    pass


class OperationalError(DatabaseError):
    """ 数据库操作错误（如断开连接） """
    pass


class IntegrityError(DatabaseError):
    """ 关系完整性错误（如外键约束失败） """
    pass


class InternalError(DatabaseError):
    """ 数据库内部错误（如游标无效） """
    pass


class ProgrammingError(DatabaseError):
    """ SQL 语法/参数错误（如表不存在） """
    pass


class NotSupportedError(DatabaseError):
    """ 不支持的特性（如调用 rollback 但事务不支持） """
    pass
