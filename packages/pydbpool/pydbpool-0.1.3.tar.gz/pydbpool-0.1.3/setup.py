# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : setup.py
@Project  : 
@Time     : 2025/3/18 11:27
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pydbpool",
    version="0.1.2",
    author="dylan",
    author_email="cgq2012516@163.com",
    description="A high-performance database connection pool for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pydbpool",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pydbpool = pydbpool.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
        "pymysql>=1.1.0",  # 可选，用于MySQL支持
        "psycopg2-binary>=2.9.0",  # 可选，用于PostgreSQL支持
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "mysql": ["pymysql>=1.1.0"],
        "postgresql": ["psycopg2-binary>=2.9.0"],
    },
    keywords=[
        "database",
        "connection-pool",
        "mysql",
        "postgresql",
        "sqlalchemy",
        "async",
        "thread-safe",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pydbpool/issues",
        "Documentation": "https://pydbpool.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/pydbpool",
    },
)
