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
years = ["2019", "2020", "2021"]
months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
for year in years:
    for month in months:
        # No data available yet after March 2021
        if year == "2021" and int(month) > 3:
            break
        resp = requests.get(dl_link.format(year, month)).content
        zip_data = ZipFile(BytesIO(resp))
        filename = file_template.format(year, month)
        month_df = pd.read_csv(zip_data.open(filename))
        # Print preview of data to make sure it works
        print(month_df.head())
        month_df.to_csv("./data/{}".format(filename))