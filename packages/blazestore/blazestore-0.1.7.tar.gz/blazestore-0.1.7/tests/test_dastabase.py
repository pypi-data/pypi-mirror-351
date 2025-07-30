# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/27 23:53
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

# tests/test_database.py
import pytest
import shutil
from pathlib import Path
import polars as pl

# 假设 database.py 在 blazestore 目录下
from blazestore.database import tb_path, has, put

# 临时数据路径
TEST_DB_PATH = Path("./test_data")

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """测试前准备和测试后清理"""
    # 设置测试用 DB_PATH
    from blazestore import database
    database.DB_PATH = TEST_DB_PATH

    # 创建测试目录
    TEST_DB_PATH.mkdir(exist_ok=True)
    yield

    # 清理测试目录
    if TEST_DB_PATH.exists():
        shutil.rmtree(TEST_DB_PATH)

def test_tb_path():
    """测试 tb_path 函数"""
    assert tb_path("mc/stock_kline_minute") == TEST_DB_PATH / "mc" / "stock_kline_minute"

def test_has():
    """测试 has 函数"""
    tb_dir = TEST_DB_PATH / "mc" / "stock_kline_minute"
    tb_dir.mkdir(parents=True)
    assert has("mc/stock_kline_minute") is True

    assert has("invalid_table") is False

def test_put_with_partition():
    """测试带分区字段的 put 函数"""
    tb_name = "mc/stock_kline_minute"
    df = pl.DataFrame({
        "date": ["20250401"],
        "open": [100.1],
        "high": [101.2],
        "low": [99.5],
        "close": [100.8]
    })

    put(df, tb_name=tb_name, partitions=["date"])

    expected_path = TEST_DB_PATH / "mc" / "stock_kline_minute" / "date=20250401" / "data.parquet"
    assert expected_path.exists(), "数据文件应已写入"
    loaded_df = pl.read_parquet(expected_path)
    assert df.frame_equal(loaded_df), "写入的数据应与原始数据一致"

def test_put_without_partition():
    """测试不带分区字段的 put 函数"""
    tb_name = "factor_table"
    df = pl.DataFrame({
        "factor_id": [1],
        "value": [0.85]
    })

    put(df, tb_name=tb_name)

    expected_path = TEST_DB_PATH / "factor_table" / "data.parquet"
    assert expected_path.exists()
    loaded_df = pl.read_parquet(expected_path)
    assert df.frame_equal(loaded_df)

def test_put_overwrite():
    """测试重复写入是否会覆盖"""
    tb_name = "mc/stock_kline_minute"
    df1 = pl.DataFrame({"date": ["20250401"], "value": [100]})
    df2 = pl.DataFrame({"date": ["20250401"], "value": [200]})

    put(df1, tb_name=tb_name, partitions=["date"])
    put(df2, tb_name=tb_name, partitions=["date"])

    expected_path = TEST_DB_PATH / "mc" / "stock_kline_minute" / "date=20250401" / "data.parquet"
    loaded_df = pl.read_parquet(expected_path)
    assert loaded_df["value"][0] == 200, "第二次写入应覆盖第一次内容"

def test_put_with_nested_partitions():
    """测试多级分区写入"""
    tb_name = "mc/stock_kline_minute"
    df = pl.DataFrame({
        "date": ["20250401"],
        "symbol": ["AAPL"],
        "open": [100.1],
        "close": [100.8]
    })

    put(df, tb_name=tb_name, partitions=["date", "symbol"])

    expected_path = TEST_DB_PATH / "mc" / "stock_kline_minute" / "date=20250401" / "symbol=AAPL" / "data.parquet"
    assert expected_path.exists()
    loaded_df = pl.read_parquet(expected_path)
    assert df.frame_equal(loaded_df)
