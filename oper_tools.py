# encode: UTF-8
import matplotlib.pyplot as plt
# from matplotlib import figure
import numpy
import pandas as pd
import numpy as np
import datetime
import csv
from datetime import date, timedelta
import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
import time
from calendar import monthrange, isleap
# from jdcal import jd2gcal, jcal2jd
from functools import reduce
from matplotlib import rc
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
import matplotlib.dates as mdates
import os
import sys
# import psycopg2
# import
from era2bas import append_dates

from settings import Settings
sets = Settings()


plt.style.use('ggplot')
font = {'family': 'verdana',
        'weight': 'bold',
        'size': 12}

rc('font', **font)


def graph_fcst(pathCT, pathENS, date_start, date_end, skrows, rrows):
    # ct = pd.read_csv(pathCT, header=None, skiprows=1, names=['date', 'factq', 'simq'], delimiter=r"\s+")
    # ct['Date'] = pd.to_datetime(ct['date'], format="%Y%m%d")
    # ct.index = ct['date']

    ct = pd.read_csv(r'c:\Users\morey\PycharmProjects\run_ecomag\qkabansk.txt', header=None, skiprows=1, names=['Date', 'factq', 'simq'],
                     delimiter=r"\s+", index_col='Date', parse_dates=True, dayfirst=True)

    # print(ct.head())
    # rrows = int((date_end - date_start).days)
    # ens = pd.read_csv(pathENS, header=0, delimiter=r"\s+", nrows=rrows, skiprows=[1-skrows], date_parser=['DAY'], dayfirst=True)
    # ens['DAY'] = pd.to_datetime(ens['DAY'], format="%Y%m%d")
    # ens.index = ens['DAY']
    # # print(ens)
    # del ens['DAY']

    ens = pd.read_csv(pathENS, header=0, delimiter=',', nrows=rrows, index_col='date', parse_dates=True)
    # print(ens)
    del ens['Unnamed: 0']

    # ens['date'] = pd.date_range(date_start, periods=rrows, freq='D')
    # ens.index = ens['date']
    # ens.index = ens.index.map(lambda t: t.replace(year=2017))
    # ens = ens.iloc[ens.index.month >= 4]
    # print(ens)

    cdf = ens.drop('Qmean', axis=1)
    ws = cdf.sum().sort_values() * 86400 / 1000000000
    qs = cdf.max().sort_values()
    # print(qs)
    meanw = round(np.mean(ws), 2)
    meanq = round(np.median(qs))
    w10 = round(np.percentile(ws, 10), 2)
    w90 = round(np.percentile(ws, 90), 2)
    q10 = round(np.percentile(qs, 10))
    q90 = round(np.percentile(qs, 90))
    days_above_meanq = cdf[cdf >= 4150].count().sort_values()
    days_above_maxq = cdf[cdf >= 7000].count().sort_values()
    meandavq = round(np.mean(days_above_meanq))
    meandmaxq = round(np.mean(days_above_maxq))
    mdmq10 = round(np.percentile(days_above_meanq, 10))
    mdmq90 = round(np.percentile(days_above_meanq, 90))
    mdmaxq10 = round(np.percentile(days_above_maxq, 10))
    mdmaxq90 = round(np.percentile(days_above_maxq, 90))


    step = 1 / len(ws)
    fig1, (ax1, ax2) = plt.subplots(1, 2, sharex=False, sharey=False)
    fig2, (ax3, ax4) = plt.subplots(1, 2, sharex=False, sharey=False)
    cdfwplot, = ax1.plot(ws, np.arange(0, 1, step))
    l1, = ax1.plot([meanw, meanw], [0, 1])
    ax1.set_title(r'Объем притока во II квартале, куб. км')
    l2, = ax1.plot([w10, w10], [0, 0.1], color='grey', linestyle='dashed')
    ax1.plot([w90, w90], [0, 0.9], color='grey', linestyle='dashed')

    # tt = ax1.table(cell_text=ws.describe().index.values, )
    wtable = ax1.table(cellText=[[w10, meanw, w90]], colWidths=[0.1]*3,
              colLabels=[ u'W10%', u'Wср', u'W90%'], loc='upper left')

    cdfqplot, = ax2.plot(qs, np.arange(0, 1, step))
    l3, = ax2.plot([meanq, meanq], [0, 1])
    ax2.set_title(r'Максимальный расход притока во II квартале, куб. м/с')
    l4, = ax2.plot([q10, q10], [0, 0.1], color='grey', linestyle='dashed')
    ax2.plot([q90, q90], [0, 0.9], color='grey', linestyle='dashed')
    qtable = ax2.table(cellText=[[ q10, meanq, q90]], colWidths=[0.1] * 3,
                       colLabels=[u'Q10%', u'Qср', u'Q90%'], loc='upper left')

    cdfdaavqplot = ax3.plot(days_above_meanq, np.arange(0, 1, step))
    ax3.set_title(r'Количество дней с расходом выше 4150 куб. м/с во II квартале')
    cdfdamqplot = ax4.plot(days_above_maxq, np.arange(0, 1, step))
    l5, = ax3.plot([meandavq, meandavq], [0, 1])
    l6, = ax3.plot([mdmq10, mdmq10], [0, 0.1], color='grey', linestyle='dashed')
    ax3.plot([mdmq90, mdmq90], [0, 0.9], color='grey', linestyle='dashed')
    avqtable = ax3.table(cellText=[[mdmq10, meandavq, mdmq90]], colWidths=[0.1] * 3,
                       colLabels=[u'nQ10%', u'nQср', u'nQ90%'], loc='upper left')

    ax4.set_title(r'Количество дней с расходом выше 7000 куб. м/с во II квартале')
    l7, = ax4.plot([meandmaxq, meandmaxq], [0, 1])
    l8, = ax4.plot([mdmaxq10, mdmaxq10], [0, 0.1], color='grey', linestyle='dashed')
    ax4.plot([mdmaxq90, mdmaxq90], [0, 0.9], color='grey', linestyle='dashed')
    mqtable = ax4.table(cellText=[[mdmaxq10, meandmaxq, mdmaxq90]], colWidths=[0.1] * 3,
                        colLabels=[u'nQ10%', u'nQср', u'nQ90%'], loc='upper left')

    wtable.auto_set_font_size(False)
    wtable.set_fontsize(10)
    qtable.auto_set_font_size(False)
    qtable.set_fontsize(10)
    avqtable.auto_set_font_size(False)
    avqtable.set_fontsize(10)
    mqtable.auto_set_font_size(False)
    mqtable.set_fontsize(10)

    fig1.legend([cdfwplot, l1, l2], [u'ИФР', u'Средний прогноз', u'80% ДИ'], loc='lower center')
    fig2.legend([cdfqplot, l3, l4], [u'ИФР', u'Средний прогноз', u'80% ДИ'], loc='lower center')

    # ct = ct.append(ens)
    ct = ct.join(ens, how='left')
    ct = ct.sort_index()
    # print(ct.loc[date_start:date_end])
    # ct.to_csv(r'd:\Dropbox\ИВП РАН\половодье 2017\ens.txt')

    # pic = ct.iloc[ct.index.month >= date_start.month].plot(colormap='Greys')
    pic = ct.loc[date_start:date_end].plot()
    pic.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    qsim = pic.lines[1]
    qf = pic.lines[0]
    qm = pic.lines[-1]
    qsim.set_linewidth(3)
    qsim.set_color('green')
    qf.set_linewidth(3)
    qf.set_linestyle('dashed')
    qf.set_color('blue')
    qm.set_linewidth(3)
    qm.set_color('red')
    plt.grid()
    days = mdates.DayLocator()
    pic.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=15))
    pic.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    pic.set_xlabel(r'Дата')
    pic.set_ylabel(r'Q, куб. м/с')
    pic.grid()
    # plt.title(r'График ансамблевого прогноза притока воды в Чебоксарское водохранилище за период с ' +
    #           date_start.strftime("%d.%m.%Y") + ' г. по ' + date_end.strftime("%d.%m.%Y") + ' г. ')
    pic.legend([qf, qsim, qm], [r'Obs', r'Forуcast', r'Ensemble mean'], loc='center right')
    plt.plot(['1991-07-01', '1991-10-01'], [0, 6000], 'k-', lw=1)
    # plt.text('1991-03-27', 13000, r'Дата выпуска прогноза', rotation=90)
    # plt.text('1991-02-05', 14000, 'Расчет начальных условий \n по фактической метеорологии')
    # plt.text('1991-05-05', 14000, 'Прогноз притока по ансамблю \n наблюдавшихся сценариев')
    plt.show()

def check_meteo(path, date_start):
    # префиксы файлов
    met_vars = ['TEMP', 'PRE']
    flag = []
    # цикл по переменным
    for i, v in enumerate(met_vars):
        # print(i, v)
        # путь до файла с текущим годом
        met_file =  path + '/' + v + str(date_start.year)[2:4] + '.bas'
        # читаем из файла список станций
        try:
            f = open(met_file)
        except FileNotFoundError:
            print('Нет данных прогноза GFS на ', date_start)
            return False
        else:
            with open(met_file) as f:
                # print(f.name)
                f.readline()
                f.readline()
                ind = f.readline().rstrip().split(sep=",")
                f.close()
            ind.insert(0, 'date')
            # ind.pop(-1)
            # print(ind)
            df = pd.read_csv(met_file, header=None, skiprows=6, delimiter=r"\s+", names=ind, parse_dates=['date'],
                            dayfirst=False, index_col='date', na_values=-99.0)
            if df.size > 0:
                nulldata = df[df.index == date_start.strftime('%Y-%m-%d')].isnull().sum(axis=1).values == len(ind) - 1
                non_nulldata = len(ind) - 1 - df[df.index == date_start.strftime('%Y-%m-%d')].isnull().sum(axis=1).values
                if nulldata:
                    print('Отсутствуют данные по ' + v + ' за дату выпуска прогноза: ' + date_start.strftime('%d.%m.%Y') + '.')
                    flag.append(False)
                else:
                    print('Данные по ' + v + ' есть за дату выпуска прогноза с ' + str(non_nulldata).strip("[]") + ' станций.')
                    flag.append(True)
            else:
                print('Отсутствуют данные по ' + v + ' за дату выпуска прогноза: ' + date_start.strftime(
                    '%d.%m.%Y') + '.')
                flag.append(False)

    if numpy.mean(flag) == 1:
        return True
    else:
        return False


def check_hydro(path, date_start):
    """
    Функция для проверки наличия файла с гидроданными за текущий год и наличия данных. Если его нет, он создается,
    но выдается предупреждение.

    :param path:            Путь до папки HYDRO
    :param date_start:      Дата выпуска прогноза
    :return:
    """
    result = False
    print(f"check hydr.bas for {path} at {date_start}")
    # если дата пришла как строка, преобразуем в дату
    if isinstance(date_start, str):
        date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
    # путь до файла с текущим годом
    hyd_file = path + '\\hydr' + str(date_start.year)[2:4] + '.bas'
    # читаем из файла список станций
    if os.path.exists(hyd_file):
        df = pd.read_csv(hyd_file, header=None, skiprows=3, delimiter=r"\s+|\t+", parse_dates=[1], date_format ='%Y%m%d',dayfirst=True, index_col=[1],
                     na_values=-99.0, engine='python')


    # print(df.head())
    # nans = df[2].isnull().sum()
        nulldata = df[df.index == (date_start - datetime.timedelta(days=1)).strftime('%Y-%m-%d')][2].isnull()

        if nulldata.values == True:
            print('Отсутствуют данные по расходам воды на дату выпуска прогноза: ' + date_start.strftime('%d.%m.%Y') + '.')
        # app_log.error(
        #     'Отсутствуют данные по расходам воды на дату выпуска прогноза: ' + date_start.strftime('%d.%m.%Y') + '.')

        else:
            print('Данные по расходам воды есть на дату выпуска прогноза ' + date_start.strftime('%d.%m.%Y') + '.')
            result = True
        # app_log.error(
        #     'Данные по расходам воды есть на дату выпуска прогноза ' + date_start.strftime('%d.%m.%Y') + '.')
    return result


def readShort(path, **kwargs):
    # path = 'd:/EcoBaikal/Archive/002/RES/20250424/QCURVBaikal                        .txt',
    df = pd.read_csv(path,
                     sep='\s+', names=['date', 'angara', 'barguzin', 'selenga', 'baikal'],
                     usecols=[0, 2, 3, 4, 5], skiprows=1,
                     parse_dates=['date'], date_format='%Y%m%d')
    df.insert(0, 'lag', range(0, len(df)))

    if kwargs.get('coef') == True:
        df = pd.melt(df, id_vars=['lag', 'date']).reset_index()
        coef = pd.read_csv(os.path.join(sets.MODEL_BAS_DIR, 'X10_corr.bas'), sep=';')
        df = pd.merge(df, coef, 'left', left_on=['variable', 'lag'], right_on=['river', 'lag'])
    return df

def readCoef(path):
    df = pd.read_csv(path, sep=';')
    return df

def short_corr(date, res, pathCoeff, pathFactQ):
    '''
    Коррекция расчетных значений прогнозов по притокам и создание файлов sbrosXX.bas для Байкала
    :param date:
    :param pathCoeff:
    :param pathFactQ:
    :return:
    '''
    prog = readShort(res, coef=True)
    # print(prog.head())
    coef = readCoef(pathCoeff)
    # print(coef.head())
    df = pd.read_excel(pathFactQ)
    dateMin = prog.date.min()
    df_corr = pd.merge(prog, df.loc[df['date'] == dateMin], 'left',
                       left_on=['date', 'river'],
                       right_on=['date', 'post'])
    df_corr.loc[:, 'q'] = df_corr.loc[:, 'q'].ffill()
    df_corr['qcorr'] = df_corr['value'] + (df_corr['q'] - df_corr['value']) * df_corr['b']
    df_corr['date'] = df_corr['date'].dt.date
    df_corr = df_corr.loc[df_corr['river'] != 'baikal', ["date", "river", "qcorr"]]
    df_corr['date'] = pd.to_datetime(df_corr['date'], format='%Y%m%d')
    df_corr = df_corr.pivot(index='date', columns='river', values='qcorr')
    df_corr.rename({'river': 'riv', 'qcorr': 'q'}, axis=1, inplace=True)
    # берем фактические расходы по створам до даты начала прогноза, соединяем с прогнозами, пишем в sbros.bas
    df_fact = pd.DataFrame()
    riv = {'Anga': 'angara', 'Barg': 'barguzin', 'Sele': 'selenga'}
    for r, name in riv.items():
        # print(name)
        path = os.path.join(sets.EMG_HYDRO_DIR,r,'hydr' + str(date.year)[2:4] + '.bas')
        df = pd.read_csv(path, sep='\t+', skiprows=3, names=['n', 'date', 'q'], usecols=['date', 'q'], engine='python')
        df['riv'] = name
        df_fact = pd.concat([df_fact, df], axis=0)
        # print(df_fact.head())
    df_fact['date'] = pd.to_datetime(df_fact['date'], format='%Y%m%d')
    df_fact = df_fact.pivot(index='date', columns='riv', values='q')
    df_fact = df_fact[:date]
    df_fact = pd.concat([df_fact, df_corr], axis=0, ignore_index=False)
    # df_fact = append_dates(df_fact)
    for column in df_fact:
        # print(column)
        #path = 'c:/EcoBaikal/Data/Hydro/Baikal/' + str([k for k, v in riv.items() if v == column][0])
        path = sets.EMG_HYDRO_DIR + str([k for k, v in riv.items() if v == column][0])
        # print(path)
        writeHydr(df_fact[column], path, sbros=True, name=column)
    # print(df_fact.head())


def makeHydr(path):
    '''
    Преобразование файла от Бурятского ЦГМС / Эн+ в hydrXX.bas
    :param path:
    :return:
    '''
    df = pd.read_excel(path, names=['date','post','lev','q'], nrows=5)

    year = df['date'].dt.date.min().year
    riv = {'Anga': 'angara', 'Barg': 'barguzin', 'Sele': 'selenga'}
    trans = {'Anga': 'Верхняя Заимка', 'Barg': 'Баргузин', 'Sele': 'Селенга Мостовой'}
    for r, name in riv.items():
        outfile = sets.EMG_HYDRO_DIR + r + '/hydr' + str(year)[2:4] + '.bas'
        if os.path.exists(outfile):
            hydr_df = pd.read_csv(outfile, sep='\t', skiprows=3, names=['n', 'date', 'q'], usecols=[1, 2])
            hydr_df['date'] = pd.to_datetime(hydr_df['date'], format='%Y%m%d')
        else:
            hydr_df = pd.date_range(start=str(year) + '-01-01',
                                  end=str(year) + '-12-31')
            hydr_df = pd.DataFrame(hydr_df, columns=['date'])
            hydr_df['q'] = numpy.nan
            #hydr_df = hydr_df.set_index(['date'])


        #out = df.loc[df['post'] == trans[r]].reset_index().drop(['index', 'lev', 'post'], axis=1)
        out = df.loc[df['post'] == trans[r]].reset_index().drop(['lev', 'post'], axis=1)
        for index, row in out.iterrows():
            hydr_df.loc[hydr_df['date'] == row['date'],'q'] = row['q']
        writeHydr(hydr_df, os.path.join(sets.EMG_HYDRO_DIR, r), name=name)
        #writeHydr(out, os.path.join(sets.EMG_HYDRO_DIR,r), name=name, sbros=True)

        #writeHydr(out, 'D:/EcoBaikal/Data/Hydro/Baikal/' + r + '/', name=name, sbros=True)
        # out.index += 1
        # out.to_csv(outfile, date_format = '%Y%m%d', sep='\t', na_rep='-99.0',
        #            quoting=csv.QUOTE_NONE, escapechar=' ',
        #            header=['Basin	' + name + '	Year	' + str(year) +
        #                    ' \n 	1	0	21100 \n N	DATE	Qm3/s', '.'])
        print(name, outfile)


def writeHydr(df, path, **kwargs):
    if not os.path.isdir(path):
        os.mkdir(path)

    if 'date' in df:
        year = df['date'].dt.date.min().year
    else:
        year = df.index.min().year
    if kwargs.get('sbros') == True:
        outFile = path + '/sbros' + str(year)[2:4] + '.bas'
    else:
        outFile = path + '/hydr' + str(year)[2:4] + '.bas'

    if kwargs.get('name'):
        header = ['Basin	' + kwargs.get('name')[0] + '	Year	' + str(year) +
         ' \n 	1	0	21100 \n N	DATE	Qm3/s', '.']
    else:
        header = ['Basin	Generic	Year	' + str(year) +
         ' \n 	1	0	21100 \n N	DATE	Qm3/s', '.']



    if isinstance(df.index, pd.DatetimeIndex):
        # df['date'] = df.index
        df = append_dates(df)
        df = df.reset_index()
        df.index += 1
    else:
        df.index += 1
    df.to_csv(outFile, date_format='%Y%m%d', sep='\t', na_rep='-99.0',
               quoting=csv.QUOTE_NONE, escapechar=' ',
               header=header, float_format='%.2f')


def classify_post(post):
    match post:
        case _ if post == 'Селенга Улан-Удэ':
            return 'ulanude'
        case _ if post == 'Селенга Мостовой':
            return 'selenga'
        case _ if post == 'Баргузин':
            return 'barguzin'
        case _ if post == 'Верхняя Заимка':
            return 'angara'
        case _:
            return 'Unknown'


def readQFact(path):
    df = pd.read_excel(path, skiprows=0, names=['date', 'post', 'lev', 'q'])
    df['post'] = df['post'].apply(classify_post)
    return df


def graphShort(res):
    prog = readShort(res)
    # таблица
    prog['date'] = prog['date'].dt.date
    prog.drop('lag', axis=1).to_excel(sets.SHORT_RES + '/' + (prog['date'][0] + timedelta(days=10)).strftime("%Y%m%d") +
                                      '/' + 'x+10.xlsx', index=False)
    # рисунок
    axes = prog.drop('lag', axis=1).plot(x='date', style='.-', layout=(2, 2), subplots=True, figsize=(20, 10),
                                       title = 'Прогноз притока в Иркутское вдхр. от ' +
                                               prog['date'][0].strftime("%d.%m.%Y"), xlabel='Дата',
                                       sharex=True, grid=True, legend=False)
    # устанавливаем формат подписей по оси ординат
    axes[0, 0].set(ylabel='Расход, м$^3$/с', title='В.Ангара')
    axes[0, 1].set(ylabel='', title='Баргузин')
    axes[1, 0].set(ylabel='Расход, м$^3$/с', title='Селенга')
    axes[1, 1].set(ylabel='', title='оз.Байкал')
    # устанавливаем частоту и формат подписей дат
    loc = mdates.DayLocator(interval=1)
    fmt = mdates.DateFormatter('%d\n%b')
    for ax in axes.reshape(-1):
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(fmt)
    #plt.show()
    plt.savefig(sets.SHORT_RES + '/' + (prog['date'][0] + timedelta(days=10)).strftime("%Y%m%d") + '/' +
                'x+10' + '.png', dpi=200, bbox_inches='tight')


def dec_quantile(df):
    '''

    :param df:
    :return:
    '''
    q10 = round(np.percentile(df.mean(axis=1), 10), 2)
    q25 = round(np.percentile(df.mean(axis=1), 25), 2)
    q75 = round(np.percentile(df.mean(axis=1), 75), 2)
    q90 = round(np.percentile(df.mean(axis=1), 90), 2)
    return [q10, q25, q75, q90]


def long_corr(df, type):
    '''

    :param df:
    :param type:
    :return:
    '''
    # df.plot(kind='line')
    df = df.drop('Qmean', axis=1)
    df['arg'] = (len(df) - df.reset_index().index.values) / len(df)
    df['date'] = df.index
    df = df.melt(id_vars=['date', 'arg'], var_name='scenario', value_name='q')
    path = os.path.join(sets.SHORT_RES, df['date'].min().strftime('%Y%m%d'),
                        sets.SOURCE_NAME)
    ct = readShort(path)
    df = df.merge(ct[['date', 'baikal']], on='date', how='outer')
    df['qcor'] = df['q'].case_when(caselist=[
        (df['date'] <= ct['date'].max(), df['baikal']),
        (df['date'] > ct['date'].max(),
         df['q'] - df['arg'] * (df['q'] - df['baikal'].loc[df['date'] == ct['date'].max()].values))
    ])
    df.loc[df['scenario'].isnull(), 'scenario'] = 'Qmean'
    df = df.pivot(index='date', columns='scenario', values='qcor')
    df['Qmean'] = df.mean(axis=1)
    # df.plot(kind='line')
    print(df.head())
    return(df)


def ens_stat(path):
    '''

    :param path:
    :return:
    '''
    df = pd.read_csv(path, header=0)
    del df['Unnamed: 0']
    df.index = df['date']
    df.index = pd.to_datetime(df.index)
    del df['date']
    del df['fact']
    df.drop(df.tail(1).index, inplace=True)
    dfw = df * 86400 / 1000000000

    # коррекция по краткосрочному прогнозу
    df = long_corr(df, type='1')

    month_q = df.drop('Qmean', axis=1).resample('ME').mean().transpose().describe(
        percentiles=[.05, .5, .95]).transpose()
    month_w = dfw.drop('Qmean', axis=1).resample('ME').sum().transpose().describe(
        percentiles=[.05, .5, .95]).transpose()
    qmax_date = df.drop('Qmean', axis=1).idxmax()
    qmax_date = qmax_date.describe()
    del month_w['count']
    del month_q['count']

    month_w.index = month_w.index.to_period('M')
    month_w['period'] = month_w.index.strftime("%B")

    # quarter_w['period'] = quarter_w.index.strftime("%q") + ' квартал '
    month_q.index = month_q.index.to_period('M')
    month_q['period'] = month_q.index.strftime("%B")

    month_w['var'] = 'W'
    month_q['var'] = 'Q'

    f = os.path.dirname(os.path.abspath(path)) + '//' + 'stats_' + df.index.min().strftime("%Y-%m-%d") + '.csv'
    with open(f, 'w+') as filer:
        filer.write('Объем притока км3 \n')
        filer.close()
    month_w.to_csv(f, mode='a', header=True, float_format='%.3f', encoding='windows-1251')
    with open(f, "a+") as filer:
        filer.write('Средний расход воды притока м3/сек \n')
        filer.close()
    month_q.to_csv(f, mode='a', header=True, float_format='%.3f', encoding='windows-1251')
    with open(f, "a+") as filer:
        filer.write("\n")
        filer.write("Наиболее вероятная дата пика: " + qmax_date['mean'].strftime("%d.%m.%Y") + "\n")
        filer.write("Ранняя дата пика: " + qmax_date['min'].strftime("%d.%m.%Y") + "\n")
        filer.write("Поздняя дата пика: " + qmax_date['max'].strftime("%d.%m.%Y") + "\n")
        filer.close()

    pd.concat([month_w, month_q])
    # p = os.path.dirname(os.path.abspath(path)) + '//' + 'stats.pkl'
    # month_w.to_pickle(p)

    # графика
    fig, axs = plt.subplots(2, 1, figsize=(15, 15))
    # month_w.plot(ax=axs[0, 0], y='mean', kind='bar', rot=0,
    #              yerr=[month_w['mean']-month_w['5%'], month_w['95%']-month_w['mean']], capsize=6)
    # # axs[0, 0].legend(['Средний прогноз'])
    # axs[0, 0].legend(['Mean'])
    # axs[0, 0].set_xlabel('')
    # # axs[0, 0].set_ylabel(r'Объем притока, км$^3$')
    # axs[0, 0].set_ylabel('Inflow volume, km$^3$')

    month_q.plot(ax=axs[0], y='mean', kind='bar', rot=0, color='tab:blue',
                 yerr=[month_q['mean'] - month_q['5%'], month_q['95%'] - month_q['mean']],
                 error_kw=dict(ecolor='black', lw=2, capsize=5, capthick=2))
    axs[0].legend([r'Средний прогноз'])
    axs[0].set_ylabel(r'Приток, м$^3$/с')
    axs[0].set_xlabel(r'Месяц')
    axs[1].axis('off')
    axs[1].axis('off')

    # w_tbl = axs[1, 0].table(cellText=month_w[['mean', '5%', '50%', '95%']].round(2).values,
    #                         colLabels=['Средний\nпрогноз', '95%', 'Медиана', '5%'],
    #                         rowLabels=month_w.index, loc='center', bbox=[0,0,1,1])
    # w_tbl.auto_set_font_size(False)
    # w_tbl.set_fontsize(14)

    q_tbl = axs[1].table(cellText=month_q[['mean', '5%', '50%', '95%']].astype(int).values,
                         colLabels=['Средний\nпрогноз', '95%', 'Медиана', '5%'],
                         rowLabels=month_w.index, loc='center', bbox=[0, 0, 1, 1])
    q_tbl.auto_set_font_size(False)
    q_tbl.set_fontsize(14)
    fig.suptitle("Прогноз притока в Иркутское вдхр. от " + df.index.min().strftime("%d.%m.%Y"), fontsize=15)
    fig.savefig(os.path.dirname(os.path.abspath(path)) + "//" + 'graph_' + df.index.min().strftime("%Y-%m-%d") + '.png',
                dpi=100, bbox_inches='tight')
    # plt.show()

    # гидрограф
    # fig = plt.figure(figsize=[16, 10])
    # ax = fig.add_subplot()
    # df.drop('Qmean', axis=1).plot(ax=ax, legend=False, grid=True)
    # df['Qmean'].plot(ax=ax, color = 'red', lw=4)
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.1,
    #                  box.width, box.height * 0.9])
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
    #       fancybox=True, shadow=True, ncol=12)
    #
    # # линии для пиков
    # ax.axvline(qmax_date['mean'], linestyle='--', color='blue')
    # ax.text(qmax_date['mean'], month_q['max'].max(), "Наиболее вероятная дата пика: \n" + qmax_date['mean'].strftime("%d.%m.%Y"),
    #         rotation=90, verticalalignment='top', ma='right', bbox=dict(facecolor='white', alpha=0.7, lw=0))
    # ax.axvline(qmax_date['min'], linestyle='--', color='blue')
    # ax.text(qmax_date['min'], month_q['max'].max(),
    #         "Ранняя дата пика: \n" + qmax_date['min'].strftime("%d.%m.%Y"),
    #         rotation=90, verticalalignment='top', ma='right', bbox=dict(facecolor='white', alpha=0.7, lw=0))
    # ax.axvline(qmax_date['max'], linestyle='--', color='blue')
    # ax.text(qmax_date['max'], month_q['max'].max(),
    #         "Поздняя дата пика: \n" + qmax_date['max'].strftime("%d.%m.%Y"),
    #         rotation=90, verticalalignment='top', ma='right', bbox=dict(facecolor='white', alpha=0.7, lw=0))


# главный модуль
if __name__ == "__main__":
    # date = datetime.date(2022, 4, 14) + datetime.timedelta(days=10)
    # pathCoeff = 'd:/EcoBaikal/Basin/Baik/Bas/X10_corr.bas'
    # pathFactQ = 'd:/Data/Hydro/buryat_q_2022.xlsx'
    # makeHydr('d:/Data/Hydro/buryat_q_2022.xlsx')
    # short_corr(date, 'd:/EcoBaikal/Basin/Baik/Bas/X10_corr.bas', pathCoeff, pathFactQ)
    # readQFact('d:/YandexDisk/ИВПРАН/En+/отчет2025_2/1_шаблон_расчетный_среднесуточный.xlsx')
    ens_stat(r'd:\EcoBaikal\Archive\003\ENS\20250601\20250601_ens.txt')
