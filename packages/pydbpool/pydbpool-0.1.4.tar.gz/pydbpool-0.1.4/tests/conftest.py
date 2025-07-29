# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : conftest.py
@Project  : 
@Time     : 2025/3/18 13:58
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import pymysql
import pytest

from  import DBPool
from .base import PoolOption


@pytest.fixture(scope="module")
def mysql_pool():
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=2,
        # max_overflow=2,
        max_retries=2,
        pool_recycle=5,
        pool_timeout=3,

    )
    pool = DBPool(
        connect_func=pymysql.connect,
        option=opt,
        host="127.0.0.1",
        port=3306,
        user="root",
        password="2012516nwdytL!",
        database="lamtun_dev",
    )
    yield pool
    pool.close()
