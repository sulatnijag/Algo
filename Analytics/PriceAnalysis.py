# -*- coding: utf-8 -*-

import logging as log
import psycopg2
from psycopg2 import Error
import pandas as pd
from pandas.plotting import register_matplotlib_converters


import matplotlib.pyplot as plt 
import mplfinance as mpf
import matplotlib.dates as mpdates 
import pytz

register_matplotlib_converters()

#matplotlib.rcParams['figure.figsize'] = [12.0, 8.0]



date_range = pd.date_range(start='26/11/2020', end='30/11/2020', freq='H')


conn = psycopg2.connect('host=localhost user=postgres password=abcd1234')
log.info("Connected to database")

#cur = conn.cursor()
#cur.execute(r'select count(*) from "fxDB".tbl_fx_majors')
query = """
            select time_utc, bid from "fxDB".tbl_fx_majors
            where epic = 'CHART:CS.D.EURUSD.CSD.IP:TICK'
            order by time_utc desc
            
        """
df = pd.read_sql(query, con=conn)
                      
df = df.set_index('time_utc')


conn.close()


df_ohlc_hourly = df.resample('10T').agg({'bid': ['first','max','min','last']})
df_ohlc_hourly.rename(columns={'first':'Open','max':'High', 'min':'Low', 'last':'Close'}, inplace=True)


sg_time = pytz.timezone('Asia/Singapore')
ny_time = pytz.timezone('America/New_York')
ld_time = pytz.timezone('Europe/London')
df_ohlc_hourly.index = df_ohlc_hourly.index.tz_convert(ny_time)

mpf.plot(df_ohlc_hourly['bid'],type='candle')

