#!/usr/bin/env python
# coding: utf-8
import rioxarray
# import rasterio
import pandas as pd
import os
import glob
import datetime as dt
import matplotlib.pyplot as plt
import xarray as xr

# Папки с ежедневными tif-файлами
path_data = 'd:/EcoMeteo/ECMWF/'
for var in ['temperature', 'precipitation']:
    path = os.path.join(path_data, '*' + var + '.nc')
    ListDir = glob.glob(path, recursive=True)
    print(ListDir)
    for file in ListDir:
        print(file)
        xds = xr.open_mfdataset(file, decode_times=False)
        df = xds.to_dataframe()
        df = df.reset_index()
        print(path_data)