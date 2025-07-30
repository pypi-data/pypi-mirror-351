# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/27 23:54
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
import ylog

import blazestore as bs
import polars as pl

def kline_minute(date):
    query = f"""
    select replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
               EventDate                                                       as date, 
               formatDateTime(datetime, '%T')                                  as time,
               total_turnover                                                  as money,
               volume,
               open,
               high,
               low,
               close,
               if(num_trades < 0, 0, if(num_trades > toInt64(volume), 0, num_trades))   as num_trades
        from cquote.stock_minute_distributed final
            prewhere EventDate = '{date}'
        order by asset;
    """
    return bs.read_ck(query)

fac_kline_minute = bs.Factor(fn=kline_minute)

if __name__ == '__main__':
    date = "2025-05-06"
    # val = fac_kline_minute.get_value(date)
    # ylog.info(val)
    # fac_kline_minute.info()
    # print(fac_kline_minute.name)
    # df = bs.sql(f"select * from {fac_kline_minute.tb_name} where date='{date}';")
    df = fac_kline_minute.get_value(date)
    db = bs.from_polars(df, align=False)
    # ylog.info(df.collect())
    import time
    db.sql("ind_pct(close) as roc")
    start_t = time.time()
    res = db.sql("ind_ewmmean(roc, 20)",
           "ind_std(ind_ewmmean(roc, 20), 30)",
           "ind_ewmmean(ind_std(ind_ewmmean(roc, 20), 30), 20)",
           )
    ylog.info(res)
    # pl.col("").collect()
    ylog.info(f"cost {(time.time()-start_t):.3f}s")
    start_t = time.time()
    res = db.sql("ind_ewmmean(roc, 20) as roc_20",
           "ind_std(roc_20, 30) as roc_20_sd30",
           "ind_ewmmean(roc_20_sd30, 20)")
    ylog.info(f"cost {(time.time()-start_t):.3f}s")
    ylog.info(res)

