# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : demo.py
@Project  : 
@Time     : 2025/3/20 19:21
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
import random
import threading
import time
import logging
from functools import wraps
from typing import Any, Callable, Deque, Dict, Set, Type
from collections import deque
from contextlib import contextmanager


from .dbpool import DBPool

from .errors import PoolExhaustedError, PoolClosedError, PoolTimeoutError
from .base import BaseConnection, BasePool, PoolOption, DBPoolMeta
from .dbconnection import DBPoolConnection


def exec_sql(p: DBPool, text, idx):
    _con = p.get_connection()
    _cur = _con.cursor()
    _cur.execute(text)
    print(f'sleep===>{idx}:', _cur.fetchall()[0])
    p.release_connection(_con)


def split_total(total: int, parts: int) -> list[int]:
    # 生成 (parts-1) 个分割点，范围在 [1, total-1]
    dividers = sorted(random.sample(range(1, total), parts - 1))
    # 计算每个区间的长度（即每个部分的值）
    result = [dividers[0]]  # 第一个数
    for i in range(1, parts - 1):
        result.append(dividers[i] - dividers[i - 1])  # 中间数
    result.append(total - dividers[-1])  # 最后一个数
    return result


def monitor(p: DBPool):
    text = """select count(*) from information_schema.PROCESSLIST;"""
    while True:
        time.sleep(1)
        print(json.dumps(p.meta.as_dict(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    import pymysql

    sql = """SHOW FULL PROCESSLIST;"""
    opt = PoolOption(
        minsize=1,
        maxsize=3,
        max_usage=3,
        # max_overflow=2,
        max_retries=2,
        pool_recycle=5,
        # pool_timeout=3,

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

    threading.Thread(target=monitor, args=(pool,), daemon=True).start()

    texts = [f"select sleep({i});" for i in split_total(600, 60)]
    print(texts)
    for i, t in enumerate(texts, start=1):
        threading.Thread(target=exec_sql, args=(pool, t, i), daemon=True).start()

    time.sleep(3600)
    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        print(cursor.fetchall())