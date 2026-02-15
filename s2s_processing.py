#!/usr/bin/env python
# coding: utf-8
import rioxarray
# import rasterio
import pandas as pd
import os
import glob
import datetime as dt
import matplotlib.pyplot as plt
import xarray

# Папки с ежедневными tif-файлами
path_data = 'd:/EcoMeteo/ECMWF/'

TempListDir = glob.glob(os.path.join(path_data, '*temperature.nc'), recursive=True)

xds = xarray.open_dataset(TempListDir[1])
df = xds.to_dataframe()
df = df.reset_index()

print(path_data)