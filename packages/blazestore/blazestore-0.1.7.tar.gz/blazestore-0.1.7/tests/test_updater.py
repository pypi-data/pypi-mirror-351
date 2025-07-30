# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/27 23:53
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import blazestore as bs
import polars as pl
from glob import glob

from blazestore import tb_path
from pathlib import Path
import os


# df = pl.scan_delta(str(bs.tb_path("聚源数据/上市信息")))
# # pl.sql
# polars.sql.register("detal_table", df)
#
if __name__ == '__main__':
    # res = bs.sql("select * from 聚源数据/上市信息", lazy=False)
    # pl.LazyFrame().
    # print(res)
    # print(res.select(pl.col("_metadata")))
    # import time
    # tbpath = tb_path("mc/kline_stock_minute")
    # start_t = time.time()
    # # tbpath=tb_path("聚源数据/上市信息")
    # partition_dirs = glob(str(tbpath/ "date=*"), )
    # print(f"cost {(time.time()-start_t):.3f} s")
    # print(set(os.path.relpath(p, tbpath).split("=")[-1] for p in partition_dirs))
    # partition_values = [os.path.relpath(p, tbpath) for p in partition_dirs]
    # print(partition_dirs)
    # start_t = time.time()
    # bs.sql(f"select date from mc/kline_stock_minute;").select("date").unique().collect()["date"].to_list()
    # print(f"cost {(time.time()-start_t):.3f} s")
    # start_t = time.time()
    # bs.sql(f"select date, count() as num from mc/kline_stock_minute group by date having num>0;").collect()
    # print(f"cost {(time.time()-start_t):.3f} s")
    a = None
    print(not a)


