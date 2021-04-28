# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 12:39:31 2021

@author: ahmed
"""

import pandas as pd
from zipfile import ZipFile
import requests
from io import BytesIO
from pathlib import Path

Path("./data").mkdir(exist_ok=True)

bluebikes_stations = pd.read_csv("https://s3.amazonaws.com/hubway-data/Hubway_Stations_as_of_July_2017.csv")
bluebikes_stations.to_csv("./data/bluebike-stations-july-2017.csv")

# link to where bluebikes data is stored
dl_link = 'https://s3.amazonaws.com/hubway-data/{}{}-bluebikes-tripdata.zip'
file_template = '{}{}-bluebikes-tripdata.csv'
# Collect 3 years worth of data 
months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
dt_cols = ["starttime","stoptime"]
exception_end = pd.to_datetime("2021-01-01 05:00:00", 
                                 format="%Y-%m-%d %H:%M:%S")
for year in ("2019","2020"):
    for month in months:
        resp = requests.get(dl_link.format(year, month)).content
        zip_data = ZipFile(BytesIO(resp))
        filename = file_template.format(year, month)
        month_df = pd.read_csv(zip_data.open(filename))
        for dt_col in dt_cols:
            month_df[dt_col] = pd.to_datetime(month_df[dt_col])
        # Print preview of data to make sure it works
        print(month_df.head())
        month_df.to_csv("./data/{}".format(filename),
                        index_label="row_num")
# 2021 time data is shifted 5 hours ahead
# To correct this, remove rows corresponding to first 5 hours of 2021
# and adjust all time data by subtracting 5 hours
year = 2021
dfs_2021_list = []
for month in ("01", "02", "03"):
    resp = requests.get(dl_link.format(year, month)).content
    zip_data = ZipFile(BytesIO(resp))
    filename = file_template.format(year, month)
    month_df = pd.read_csv(zip_data.open(filename))
    for dt_col in dt_cols:
        month_df[dt_col] = pd.to_datetime(month_df[dt_col])
    if month == "01":
        month_df = month_df[month_df['starttime'] >= exception_end]
    for dt_col in dt_cols:
        month_df[dt_col] = month_df[dt_col] - pd.Timedelta(hours=5)
    month_df.reset_index(inplace=True, drop=True)
    dfs_2021_list.append(month_df)
df_2021 = pd.concat(dfs_2021_list, ignore_index=True)
for month in ("01", "02", "03"):
    month_mask = df_2021['starttime'].map(lambda t: t.month) == int(month)
    month_df = df_2021[month_mask]
    print(month_df.head())
    filename = file_template.format("2021", month)
    month_df.to_csv("./data/{}".format(filename),
                    index_label = "row_num")