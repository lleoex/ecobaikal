# -*- coding: utf-8 -*-
import datetime

import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from gfs2bas import makeFcstBas
from ecobaikal_shortterm import datelist
import os
import re

# Set PROJ environment variable before importing other geospatial libraries
os.environ['PROJ_LIB'] = r'c:\Users\morey\miniconda3\envs\ecomag\Library\share\proj'  # Windows

def geotiff_to_point_shapefile(geotiff_path, output_shapefile, band=1, include_nodata=False):
    """
    Convert GeoTIFF grid coordinates to point shapefile.
    Each pixel center becomes a point feature.

    Parameters:
    -----------
    geotiff_path : str
        Path to input GeoTIFF file
    output_shapefile : str
        Path for output shapefile
    band : int, optional
        Band to extract values from (default: 1)
    include_nodata : bool, optional
        Whether to include nodata pixels (default: False)
    """

    with rasterio.open(geotiff_path) as src:
        # Read the specified band
        data = src.read(band)
        transform = src.transform
        nodata = src.nodata

        # Get raster dimensions
        height, width = data.shape

        # Create lists to store geometries and attributes
        geometries = []
        rows = []
        cols = []

        print(f"Processing raster {width}x{height} pixels...")

        # Iterate through each pixel
        for row in range(height):
            for col in range(width):

                # # Skip nodata values if specified
                # if not include_nodata and value == nodata:
                #     continue
                # if include_nodata and value == nodata:
                #     value = None

                # Convert pixel coordinates to geographic coordinates
                x, y = transform * (col + 0.5, row + 0.5)  # Center of pixel

                # Create point geometry
                point = Point(x, y)

                # Store data
                geometries.append(point)

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'geometry': geometries
    }, crs=src.crs)
    gdf['n'] = gdf.index + 1
    # Save to shapefile
    gdf.to_file(output_shapefile)
    print(f"Shapefile created: {output_shapefile}")
    print(f"Total points: {len(gdf)}")

    return gdf

def extract_geotiff_to_points(geotiff_path, shapefile_path, band=1, value_column_name='value'):
    """
    Extract values from GeoTIFF to points from shapefile and return as DataFrame.

    Parameters:
    -----------
    geotiff_path : str
        Path to the GeoTIFF file
    shapefile_path : str
        Path to the shapefile containing points
    band : int, optional
        Band number to extract from (default: 1)
    value_column_name : str, optional
        Name for the extracted value column (default: 'extracted_value')

    Returns:
    --------
    pandas.DataFrame
        DataFrame with original point attributes and extracted values
    """

    # Read the shapefile
    print("Reading shapefile... %s" % shapefile_path)
    gdf = gpd.read_file(shapefile_path)

    # Check if the shapefile contains points
    if not all(gdf.geometry.type == 'Point'):
        raise ValueError("Shapefile must contain Point geometries")

    # Open the GeoTIFF file
    print("Opening GeoTIFF...%s" % geotiff_path)
    with rasterio.open(geotiff_path) as src:
        # Extract coordinates from the points
        coords = [(point.x, point.y) for point in gdf.geometry]

        # Sample the raster at point locations
        print("Extracting values...")
        sampled_values = list(src.sample(coords, band))

        # Convert to numpy array and flatten
        sampled_values = np.array(sampled_values).flatten()

        # Handle no-data values
        sampled_values[sampled_values == 0] = np.nan
        nodata = src.nodata
        if nodata is not None:
            sampled_values = np.where(sampled_values == nodata, np.nan, sampled_values)

    # get or calculate exact date
    datestring = os.path.basename(geotiff_path)
    if datestring.find('+') < 0:
        date = pd.to_datetime(datestring[0:8])
    else:
        from_str = datestring.find('+') + 1
        to_str = datestring.find('.')
        horizon = int(datestring[from_str:to_str])
        date = pd.to_datetime(datestring[0:10]) + datetime.timedelta(days=horizon)

    # Create output dataframe from sampled values and transpose to row
    result_df = pd.DataFrame(sampled_values)
    result_df.index += 1
    if datestring.find('+') < 0 and value_column_name == 'prec':  # обработка файлов с осадками
        result_df = result_df * 1000
    elif datestring.find('+') < 0 and value_column_name == 'temp':
        result_df = result_df - 273.15
    result_df = result_df.T
    # Add date as first column
    result_df.insert(0, 'date', date)
    # result_df.date = pd.to_datetime(result_df.date)

    print(f"Successfully extracted values for {len(result_df)} points")
    return result_df


def filename_gen_by_date(init_date, rean_path, gfs_path, var):
    init_date = pd.to_datetime(init_date)
    # strings for dates of reanalysis
    rean = pd.date_range(start=datetime.date(init_date.year, 5, 1),
                         end=init_date - datetime.timedelta(days=9)).strftime("%Y%m%d").tolist()
    rean = [rean_path + var + '/' + i for i in rean]
    # strings of dates for GFS 0 horizon
    gfs0 = pd.date_range(start=init_date - datetime.timedelta(days=8), end=init_date)
    gfs0 = [gfs_path + var + '/' + i + '+0' for i in gfs0.strftime('%Y-%m-%d')]
    # strings of dates for GFS forecast
    fcst = [gfs_path + var + '/' + init_date.strftime("%Y-%m-%d") + '+' + str(i) for i in range(1, 10)]

    flist = [i + '.tif' for i in rean + gfs0 + fcst]
    return flist

# Example usage - extract tiff values to points
if __name__ == "__main__":
    # File paths
    geotiff_file = r"d:\Data\ERA5Land\prec\20250824.tif"
    shapefile_file = r"d:\Data\GFS\gfs_points.shp"
    toDir = 'D:/1'
    reanDir = 'D:/Data/ERA5Land/'
    gfsDir = 'D:/Data/GFS/'
    var = ['temp', 'prec']
    # today = '2025-05-10'
    dates = []
    for y in range(2025, 2026):
        dates.append(datelist(str(y) + '-08-20', str(y) + '-09-30', 'D', '1'))
    dates = [day for days in dates for day in days]

    df = pd.DataFrame()

    # for each day
    for dt in dates:
        # Extract values
        # for each value
        for v in var:
            # generate dates
            date_files = filename_gen_by_date(dt, reanDir, gfsDir, v)
            # print(date_files)
            for d in date_files:
                try:
                    result_dataframe = extract_geotiff_to_points(
                        geotiff_path=d,
                        shapefile_path=shapefile_file,
                        band=1,
                        value_column_name=v  # Custom column name
                    )
                    df = pd.concat([df, result_dataframe], ignore_index=True)


                except Exception as e:
                    print(f"Error: {e}")
            df = df.set_index('date', drop=True)
            makeFcstBas(df, toDir, v, pd.to_datetime(dt))
            # df.plot(title="DataFrame Plot")
            df.to_csv('d:\Data\extracted_values_%s.csv' % v, index=False, float_format='%.2f')
            print(df.head())



# Example usage - convert tiff to point shapefile
#     input_geotiff = r"d:\Data\GFS\prec\2025-09-01+0.tif"
#     output_shp = r"d:\Data\GFS\gfs_points.shp"
#
#     point_gdf = geotiff_to_point_shapefile(
#         geotiff_path=input_geotiff,
#         output_shapefile=output_shp,
#         band=1,
#         # value_column='elevation',
#         include_nodata=False
#     )
#
#     print("First 5 points:")
#     print(point_gdf.head())