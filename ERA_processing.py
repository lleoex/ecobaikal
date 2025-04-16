#!/usr/bin/env python
# coding: utf-8
import rioxarray
# import rasterio
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import xarray

# Папки с ежедневными tif-файлами
# path_dew = 'G:/Python_Pechora/20032013_test/dew'
path_prec = 'd:/Data/ERA5Land/prec'
path_temp = 'd:/Data/ERA5Land/temp'

coarsen = 2 # Во сколько раз укрупняется размер ячейки

TempListDir = os.listdir(path_temp) # Лист tif-файлов температур
Temp0 = rioxarray.open_rasterio(path_temp + '/' + TempListDir[0]) # Открываем первый из них
Temp0 = Temp0.where(Temp0 > 0) # Исключаем нулевые значения (для акваторий)
Temp0_coarsed = Temp0.coarsen(x = coarsen, y = coarsen, boundary = 'pad').mean() # Меняем его разрешение с осреднением
# Temp0_coarsed.plot() # выводим

# Делаем то же самое с осадками
PrecListDir = os.listdir(path_prec)
Prec0 = rioxarray.open_rasterio(path_prec + '/' + PrecListDir[0])
Prec0 = Prec0.where(Prec0 > 0)
# Prec0.plot()
Prec0_coarsed = Prec0.coarsen(x = coarsen, y = coarsen, boundary = 'pad').mean()
# Prec0_coarsed.plot()

# Делаем то же самое для осадков
ListFilesPrec = os.listdir(path_prec) # Список файлов tif на каждую дату

ListToConcat1 = [] # пустой список для записи фреймов за каждую дату

for f in ListFilesPrec: # цикл по файлам   
    print(f)
    d = dt.datetime.strptime(f.split('.')[0], '%Y%m%d') # Извлекаем из названия дату (без расширения), переводим её в нужный формат    
    
    Grid = xarray.open_rasterio(path_prec + '/' + f) # Открываем текущий tif-файл
    Grid = Grid.where(Grid > 0)
    Grid = Grid.coarsen(x = coarsen, y = coarsen, boundary = 'pad').mean()    
    Df = Grid[0].to_pandas() # преобразуем его во фрейм
    Df = Df.reset_index() # убираем индекс
    
    Df.columns[1:len(Df.columns)] # В названиях колонок оставляем только долготы без бывшего индексного поля широт
    
    
    ListToConcat2 = [] # фрейм для записи фреймов со значениями для каждой долготы
    for x in Df.columns[1:len(Df.columns)]: # проходим по долготам        
        c_df = pd.DataFrame() # Создаём пустой фрейм для добавления
        c_df['y'] = Df['y'] # добавляем в него столбец со значениями широт
        c_df['x'] = x # текущую долготу
        c_df[d] = Df[x] # столбец с температурами на данной долготе с названием текущей даты
        ListToConcat2.append(c_df) # добавляем в список
    PrecDay = pd.concat(ListToConcat2) # объединяем по строкам
    PrecDay['n'] = range(1, PrecDay.shape[0] + 1) # Присваиваем каждой ячейке с уникальными широтой и долготой номер
    
    Coord = PrecDay[['n', 'x', 'y']] # Делаем для этого отдельный фрейм
    
    PrecDay = PrecDay[['n', d]] # оставляем только номер для связи и температуры на текущий день
    PrecDay = PrecDay.set_index('n') # устанавливаем индекс в качестве номера
    PrecDay = PrecDay.T # Транспонируем фрейм
    ListToConcat1.append(PrecDay) # добавляем в список
    
PrecDF = pd.concat(ListToConcat1) # объединяем все фреймы за год


# In[23]:


PrecDF.head()


# In[24]:


PrecDF.tail()


# In[25]:


PrecDF = PrecDF.reset_index()


# In[26]:


PrecDF.columns[1:]


# In[27]:


ListToConcat3 = []
for i in PrecDF.columns[1:]:
    iDF = pd.DataFrame({'date': PrecDF['index'], 'n': [i for d in range(len(PrecDF['index']))], 'Precip': PrecDF[i]})
    ListToConcat3.append(iDF)
PrecDF = pd.concat(ListToConcat3)


# In[28]:


PrecDF.head()


# In[29]:


PrecDF.tail()


# In[30]:


# И температуры
ListFilesTemp = os.listdir(path_temp) # Список файлов tif на каждую дату

ListToConcat1 = [] # пустой список для записи фреймов за каждую дату

for f in ListFilesTemp: # цикл по файлам   
    print(f)
    d = dt.datetime.strptime(f.split('.')[0], '%Y%m%d') # Извлекаем из названия дату (без расширения), переводим её в нужный формат    
    
    Grid = xarray.open_rasterio(path_temp + '/' + f) # Открываем текущий tif-файл
    Grid = Grid.where(Grid > 0)
    Grid = Grid.coarsen(x = coarsen, y = coarsen, boundary = 'pad').mean()    
    Df = Grid[0].to_pandas() # преобразуем его во фрейм
    Df = Df.reset_index() # убираем индекс
    
    Df.columns[1:len(Df.columns)] # В названиях колонок оставляем только долготы без бывшего индексного поля широт
    
    
    ListToConcat2 = [] # фрейм для записи фреймов со значениями для каждой долготы
    for x in Df.columns[1:len(Df.columns)]: # проходим по долготам        
        c_df = pd.DataFrame() # Создаём пустой фрейм для добавления
        c_df['y'] = Df['y'] # добавляем в него столбец со значениями широт
        c_df['x'] = x # текущую долготу
        c_df[d] = Df[x] # столбец с температурами на данной долготе с названием текущей даты
        ListToConcat2.append(c_df) # добавляем в список
    TempDay = pd.concat(ListToConcat2) # объединяем по строкам
    TempDay['n'] = range(1, TempDay.shape[0] + 1) # Присваиваем каждой ячейке с уникальными широтой и долготой номер
    
    Coord = TempDay[['n', 'x', 'y']] # Делаем для этого отдельный фрейм
    
    TempDay = TempDay[['n', d]] # оставляем только номер для связи и температуры на текущий день
    TempDay = TempDay.set_index('n') # устанавливаем индекс в качестве номера
    TempDay = TempDay.T # Транспонируем фрейм
    ListToConcat1.append(TempDay) # добавляем в список
    
TempDF = pd.concat(ListToConcat1) # объединяем все фреймы за год


# In[31]:


TempDF.head()


# In[32]:


TempDF = TempDF.reset_index()


# In[33]:


TempDF.tail()


# In[34]:


ListToConcat3 = []
for i in TempDF.columns[1:]:
    iDF = pd.DataFrame({'date': TempDF['index'], 'n': [i for d in range(len(TempDF['index']))], 'Temper': TempDF[i]})
    ListToConcat3.append(iDF)
TempDF = pd.concat(ListToConcat3)


# In[35]:


TempDF.head()


# In[36]:


TempDF.tail()


# In[37]:


print(PrecDF.shape)


# In[38]:


# Соединяем фреймы температуры точки росы и осадков
PrecDF = PrecDF.set_index(['n', 'date'])
DewPrecDF = DewDF.join(PrecDF, lsuffix = 'l', rsuffix = 'r')


# In[39]:


DewPrecDF.head()


# In[40]:


DewPrecDF.tail() # Смотрим, что получилось


# In[42]:


DewPrecDF = DewPrecDF[['Dewpoint', 'Precip']] # Выберем без дублирующихся колонок
#DewPrecDF.columns = ['Dewpoint', 'Precip'] # Переименовываем


# In[43]:


DewPrecDF.head()


# In[44]:


DewPrecDF.tail()


# In[45]:


# Теперь присоединяем температуры
#DewPrecDF = DewPrecDF.reset_index()
TempDF = TempDF.set_index(['n', 'date'])
DewPrecTempDF = DewPrecDF.join(TempDF, lsuffix = 'l', rsuffix = 'r')


# In[46]:


DewPrecTempDF.head()


# In[47]:


DewPrecTempDF.tail()


# In[48]:


DewPrecTempDF = DewPrecTempDF.reset_index()


# In[49]:


DewPrecTempDF.head()


# In[50]:


DewPrecTempDF.tail()


# In[51]:


DewPrecTempDF['date'] = [str(d)[0:4] + str(d)[5:7] + str(d)[8:10] for d in DewPrecTempDF['date']] # Делаем даты в формате для файлов ECOMAG


# In[52]:


DewPrecTempDF.head()


# In[ ]:





# In[53]:


DewPrecTempDF.tail()


# In[54]:


# Переводим в нужные единицы
DewPrecTempDF['Dewpoint'] = DewPrecTempDF['Dewpoint'] - 273.15    

DewPrecTempDF['Precip'] = DewPrecTempDF['Precip']*1000

DewPrecTempDF['Temper'] = DewPrecTempDF['Temper'] - 273.15


# In[55]:


DewPrecTempDF.head()


# In[56]:


DewPrecTempDF.tail()


# In[57]:


import numpy as np


# In[58]:


# Считаем дефицит по температуре точки росы и фактической по формуле Магнуса
Deficit = []
for i in range(len(DewPrecTempDF['Dewpoint'])):
    ea = 6.112*np.exp((17.67*DewPrecTempDF['Dewpoint'][i])/(DewPrecTempDF['Dewpoint'][i] + 243.5))
    es = 6.112*np.exp((17.67*DewPrecTempDF['Temper'][i])/(DewPrecTempDF['Temper'][i] + 243.5))
    Def = es - ea
    Deficit.append(Def)
DewPrecTempDF['Deficit'] = Deficit


# In[59]:


DewPrecTempDF.head()


# In[60]:


DewPrecTempDF.tail()


# In[64]:


DewPrecTempDF.to_csv('G:/Python_Pechora/20032013_test/DewPrecTempDF.csv', float_format = '%3.1f')


# In[65]:


DewPrecTempDF = DewPrecTempDF[['n', 'date', 'Precip', 'Temper', 'Deficit']]
DewPrecTempDF['f'] = 0


# In[66]:


DewPrecTempDF.head()


# In[67]:


DewPrecTempDF.tail() # Смотрим, что получилось


# In[68]:


path_output = 'G:/Python_Pechora/20032013_test/CSV'


# In[69]:


Stations = set(DewPrecTempDF['n'])
Stations = list(Stations)


# In[70]:


Stations


# In[71]:


# Сохраняем данные каждой ячейки в соответствующий csv-файл
DewPrecTempDF['date'] = [int(dat) for dat in DewPrecTempDF['date']]
DewPrecTempDF['Precip'] = [round(float(p), 1) for p in DewPrecTempDF['Precip']]
DewPrecTempDF['Temper'] = [round(float(t), 1) for t in DewPrecTempDF['Temper']]
DewPrecTempDF['Deficit'] = [round(float(d), 1) for d in DewPrecTempDF['Deficit']] # Формат десятичной записи с 1 знаком после точки
DewPrecTempDF['f'] = [int(f) for f in DewPrecTempDF['f']] 
for s in Stations: # Проходим по индексам ячеек
    print(s)
    StationDF = DewPrecTempDF[DewPrecTempDF['n'] == s] # Выбираем текущую
    StationDF = StationDF[['date', 'Precip', 'Temper', 'Deficit', 'f']]
    StationDF.to_csv(path_output + '/' + str(s) + '.csv', index = False, header = False, na_rep = '-99.0')  #, float_format = '%7.2f'


# In[72]:


# Индексы и координаты ячеек также сохраняем
meteostation_path = 'G:/Python_Pechora/20032013_test/Meteostation.csv'
Coord['x'] = [round(Xc, 1) for Xc in Coord['x']]
Coord['y'] = [round(Yc, 1) for Yc in Coord['y']]
Coord.to_csv(meteostation_path, index = False)



