# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : test_exec_sql.py
@Project  : 
@Time     : 2025/3/20 19:04
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
import random
import threading
import time

import pytest

from src.pydbpool.dbpool import DBPool
from src.pydbpool.base import PoolOption
from src.pydbpool.errors import PoolTimeoutError


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


def test_exec_mysql(mysql_pool):

    with pytest.raises(PoolTimeoutError):
        threading.Thread(target=monitor, args=(mysql_pool,), daemon=True).start()

        texts = [f"select sleep({i});" for i in split_total(300, 20)]
        print(texts)
        for i, t in enumerate(texts, start=1):
            threading.Thread(target=exec_sql, args=(mysql_pool, t, i), daemon=True).start()

        time.sleep(3600)
