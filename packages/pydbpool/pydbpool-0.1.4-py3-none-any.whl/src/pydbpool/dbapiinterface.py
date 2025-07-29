# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbapiinterface.py
@Project  : 
@Time     : 2025/3/19 21:05
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from abc import ABC, abstractmethod


class Connection(ABC):
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def cursor(self):
        pass


class Cursor(ABC):
    @property
    @abstractmethod
    def description(self):
        pass  # 返回列信息的元组序列

    @property
    @abstractmethod
    def rowcount(self):
        pass  # 返回受影响的行数

    @abstractmethod
    def execute(self, sql, parameters=None):
        pass

    @abstractmethod
    def executemany(self, sql, seq_of_parameters):
        pass

    @abstractmethod
    def fetchone(self):
        pass

    @abstractmethod
    def fetchmany(self, size=None):
        pass

    @abstractmethod
    def fetchall(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def callproc(self, procname, *args):
        pass

    @abstractmethod
    def setinputsizes(self, sizes):
        pass

    @abstractmethod
    def setoutputsize(self, size, column=None):
        pass

    @abstractmethod
    def nextset(self):
        pass

    @abstractmethod
    def arraysize(self):
        pass
