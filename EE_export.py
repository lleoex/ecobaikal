#!/usr/bin/env python
# coding: utf-8
import geemap
import ee
from datetime import timedelta
import pandas as pd
from settings import Settings
from oper_tools import check_meteo
#  авторизация в GEE
#ee.Authenticate()
#ee.Initialize(project = 'iwp-dev-383806')


service_account = 'emgbaikalsac@iwp-sac-baikal.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'iwp-sac-baikal-0f874cc5b815.json')
ee.Initialize(credentials)#,project = 'iwp-sac-baikal')

sets = Settings()

def setGeom():
    # границы по пространству
    minLon = 96.5
    maxLon = 114
    minLat = 46.5
    maxLat = 57  # задаём охват нужных данных
    geom = ee.Geometry.Polygon([[[minLon, minLat],
                                 [minLon, maxLat],
                                 [maxLon, maxLat],
                                 [maxLon, minLat],
                                 [minLon, minLat]]])  # создаём геометрию области интересов
    feature = ee.Feature(geom, {})  # создаём пространственный объект без атрибутов
    geom = feature.geometry()
    # map = geemap.Map()
    # map.centerObject(geom, zoom = 5) # Задаём местоположение и масштаб
    # map.addLayer(geom)
    # map # Извлекаем геометрию, добавляем слой на карту
    return geom

def getEra(date):
    # границы по времени
    #dateStart = '2022-01-01' # если нужно с какой-то определенной даты загрузить
    dateStart = date - timedelta(days=18) # если нужно загрузить за последние 10 дней
    dateEnd = date - timedelta(days=8)
    print('Запрашиваем данные ERA5Land за ', dateStart, dateEnd)
    # границы по пространству
    geom = setGeom()
    collection = 'ECMWF/ERA5_LAND/DAILY_AGGR' # Выбираем нужный набор данных
    period = [dateStart, dateEnd] # задаём начало и конец периода
    bands = {'temp': 'temperature_2m',
             'prec': 'total_precipitation_sum'} # выбираем переменную
    for var, band in bands.items():
        coll = ee.ImageCollection(collection).filterBounds(geom).filterDate(period[0], period[1]).select(band)
        path = sets.ERA_TIFF_DIR + var  # директория для скачивания
        geemap.ee_export_image_collection(coll, path,
                                          region=geom)  # экспортируем в нужную директорию для заданной области интересов



def getGFS(date):
    # границы по времени
    dateStart = date - timedelta(days = 10)
    dateEnd = date
    print('Запрашиваем данные GFS за ', dateStart, dateEnd)
    day_list = [[6, 12, 18, 24],
                [30, 36, 42, 48],
                [54, 60, 66, 72],
                [78, 84, 90, 96],
                [102, 108, 114, 120],
                [126, 132, 138, 144],
                [150, 156, 162, 168],
                [174, 180, 186, 192],
                [198, 204, 210, 216],
                [222, 228, 234, 240]] # Заблаговременностии в часах на каждый из 10 дней вперёд, включая день выпуска
    # границы по пространству
    geom = setGeom()
    collection = 'NOAA/GFS0P25'  # Выбираем нужный набор данных
    period = [dateStart, dateEnd]  # задаём начало и конец периода
    dr = pd.date_range(period[0], period[1])
    bandTemp = 'temperature_2m_above_ground' # Канал GFS
    path = 'd:/Data/GFS/temp' # Набор данных GFS
    for d in dr: # Проходим по датам периода
        print(d)
        for i in range(len(day_list)): # далее по порядковым номерам (индексам) сроков прогноза
            gfs = ee.ImageCollection(collection).select(bandTemp).filterDate(str(d)[0:10]).filterBounds(geom).filter(ee.Filter.inList('forecast_hours', day_list[i])).mean()
            # Выбираем из коллекции нужную заблаговременность, в случае с температурой осредняем, получаем прогноз средней температуры за сутки
            geemap.ee_export_image(gfs, path + '/' + str(d)[0:10] + '+' + str(i) + '.tif', region = geom) # Экспортируем растр прогноза в текущий день и на данный срок

    bandPrec = 'total_precipitation_surface' # Осадки в кг/кв.м, что в случае с водой соответствует мм
    path = 'd:/Data/GFS/prec'
    for d in dr:
        for i in range(len(day_list)):
            gfs = ee.ImageCollection(collection).select(bandPrec).filterDate(str(d)[0:10]).filterBounds(geom).filter(ee.Filter.inList('forecast_hours', day_list[i])).sum()
            # в случае с осадками суммируем
            geemap.ee_export_image(gfs, path + '/' + str(d)[0:10] + '+' + str(i) + '.tif', region = geom)
