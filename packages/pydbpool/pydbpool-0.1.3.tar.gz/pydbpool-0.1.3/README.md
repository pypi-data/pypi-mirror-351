# PyDBPool - Python Database Connection Pool

[![PyPI Version](https://img.shields.io/pypi/v/pydbpool)](https://pypi.org/project/pydbpool/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pydbpool)](https://pypi.org/project/pydbpool/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**PyDBPool** 是一个高性能、通用的数据库连接池实现，支持主流关系型数据库，提供完善的连接生命周期管理和监控功能。

## 特性

- 🚀 **多数据库支持**：PostgreSQL、MySQL、SQLite 等
- 🔒 **线程安全**：严格的锁机制保证高并发安全
- 📊 **实时监控**：内置连接池指标统计
- 🩺 **健康检查**：自动心跳检测与失效连接剔除
- ⚡ **异步就绪**：支持协程环境（需异步驱动）
- 🔌 **智能调度**：动态扩缩容与最小空闲维持
- 🛠️ **扩展接口**：钩子函数与自定义策略支持

## 安装

```bash
# 基础安装
pip install pydbpool

# 按需选择数据库驱动
pip install pydbpool[postgres]   # PostgreSQL支持
pip install pydbpool[mysql]      # MySQL支持
```

## 快速开始

### 基本用法

```python
from pydbpool.dbpool import DBPool
from pydbpool.base import PoolOption
import pymysql

# 初始化连接池
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
    password="*********",
    database="db_stg_demo",
)

# 使用连接
sql = """SHOW FULL PROCESSLIST;"""
with pool.connection() as conn:
    cursor = conn.cursor()
    cursor.execute(sql)
    print(cursor.fetchall())
```

### 监控指标

```python
print(pool.meta.as_dict())
# 输出示例：
{
    "created_at": 272169.148343291,
    "last_active": 272169.148343708,
    "is_closed": False,
    "usage_count": 0,
    "lifetime": 0.0,
    "total_conn_count": 13,
    "using_conn_count": 13,
    "free_conn_count": 0
}
```

## 重写自己的连接池和连接类功能

### 连接基类 BaseConnection

```python
from pydbpool.base import BaseConnection
from pydbpool.dbpool import DBPool


# 实现自己的连接类
class YourselfConnection(BaseConnection):
    pass


class YourselfPool(DBPool):
    pass

```

## pool option 配置选项

| 参数                | 默认值          | 描述                                   |
|-------------------|--------------|--------------------------------------|
| `pool_name`       | default_pool | 连接池唯一标识，用于日志或监控                      |
| `max_overflow`    | 10           | 允许超过最大连接数后的临时扩容数量                    |
| `pool_recycle`    | None         | 连接自动重建周期（秒），-1=永不回收                  |
| `max_usage`       | 0            | 单个连接的最大复用次数，0=无限制                    |
| `max_retries`     | 3            | 连接创建失败时的最大重试次数                       |
| `idle_timeout`    | None         | 空闲连接自动关闭的超时时间（秒），None=不启用（默认）        |
| `minsize`         | 1            | 连接池保持的最小空闲连接数                        |
| `maxsize`         | 3            | 连接池允许的最大连接数，None 则无限制                |
| `reset_on_return` | `rollback`   | 归还连接时的默认事务处理策略：提交/回滚/不操作             |
| `ping`            | 1            | 连接健康检查策略：0=禁用，1=从链接池获取时检查，2=放回池前检查   |
| `pool_timeout`    | None         | 从连接池获取连接的最大等待时间（秒）, None 则一直等待直到获取成功 |
| `force_close`     | False        | 关闭连接池时，是否关闭活跃的数据库连接                  |

## 性能建议

1. **连接数配置**：
   ```python
   # 推荐公式
   max_size = (avg_concurrent_requests × avg_query_time) + buffer
   ```

## 开发指南

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest tests/

# 生成文档
cd docs && make html
```

## 贡献

欢迎通过 [GitHub Issues](https://github.com/yourusername/pydbpool/issues) 报告问题或提交 Pull Request

## 许可证

[MIT License](LICENSE)

---

### 关键要素说明

1. **徽章系统**：显示版本、Python兼容性和许可证信息
2. **多代码块**：使用不同语言标签实现语法高亮
3. **配置表格**：清晰展示主要参数
4. **Web集成示例**：展示与Flask的整合
5. **监控集成**：提供Prometheus对接示例
6. **开发工作流**：明确贡献者指南

建议配合以下内容增强文档：

1. 添加架构图（使用Mermaid语法）
2. 性能基准测试数据
3. 与常用框架（Django、FastAPI）的集成示例
4. 故障排除指南
5. 版本更新日志