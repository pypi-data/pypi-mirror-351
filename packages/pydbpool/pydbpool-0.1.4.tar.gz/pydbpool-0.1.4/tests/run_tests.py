# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : run_all_tests.py
@Project  : pydbpool
@Time     : 2025/3/25 10:00
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import os
import sys
import pytest


def run_database_tests(db_type=None, mode=None):
    """运行指定数据库类型的测试
    
    Args:
        db_type: 数据库类型 (mysql, postgresql, sqlite, oracle, tidb, hive, impala, doris)
        mode: 测试模式 (sync, async)
    """
    test_args = ['-xvs']
    
    if db_type and mode:
        test_path = f"{mode}/test_{mode}_{db_type}.py" if mode == "async" else f"{mode}/test_{db_type}.py"
        test_args.append(test_path)
    elif mode:
        test_args.append(f"{mode}/")
    elif db_type:
        # 运行指定数据库的同步和异步测试
        sync_path = f"sync/test_{db_type}.py"
        async_path = f"async/test_async_{db_type}.py"
        test_args.extend([sync_path, async_path])
    else:
        # 运行所有测试
        test_args.extend(['sync/', 'async/'])
    
    return pytest.main(test_args)


if __name__ == '__main__':
    # 切换到测试目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 解析命令行参数
    db_type = None
    mode = None
    
    for arg in sys.argv[1:]:
        if arg in ['mysql', 'postgresql', 'sqlite', 'oracle', 'tidb', 'hive', 'impala', 'doris']:
            db_type = arg
        elif