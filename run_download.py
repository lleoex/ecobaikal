import os.path
from os import listdir

from datetime import datetime, timedelta
import sys
import argparse
import ecobaikal_shortterm
from EE_export import getEra, getGFS
from era2bas import eraProc
from gfs2bas import gfsProc
from receiver import receivemail
import oper_tools
from settings import Settings


workdir = ""
sets = Settings()
def getQEnPlusApi(dt:datetime):
    receivemail()
    files = [f for f in listdir(sets.EMAIL_XLS_DIR) if (os.path.isfile(os.path.join(sets.EMAIL_XLS_DIR, f)) and dt.strftime('%Y%m%d') in f)]
    print(files)
    oper_tools.makeHydr(os.path.join(sets.EMAIL_XLS_DIR,files[0]))


if __name__ == '__main__':
    # today =  datetime.date.today()
    parser = argparse.ArgumentParser(description='downloader')
    parser.add_argument('--date_today', type=str, help='Дата начала расчета гггг-мм-дд', required=True)
    parser.add_argument('--source', choices=['Q', 'GFS', 'ERA'], required=True)

    args = parser.parse_args()

    src = args.source
    today = datetime.strptime(args.date_today,'%Y-%m-%d')

    result = False

    if src == "Q":
        haveQ = True
        for k in sets.rivers:
            haveQ = haveQ and oper_tools.check_hydro(os.path.join(sets.EMG_HYDRO_DIR,k),today)
        if not haveQ:
            getQEnPlusApi(today)
        #getQEnPlusApi(today)
        haveQ = True
        for k in sets.rivers:
            haveQ = haveQ and oper_tools.check_hydro(os.path.join(sets.EMG_HYDRO_DIR, k), today)
        result = haveQ
    elif src == "ERA":
        if not oper_tools.check_meteo(sets.ERA_BAS_DIR, today - timedelta(days=8)):
            getEra(today)
            # сделать bas из tifов ERA5Land
            eraProc(today)
        result = oper_tools.check_meteo(sets.ERA_BAS_DIR, today - timedelta(days=8))
    elif src == "GFS":
        while not result:
            gfs_dir_fore=os.path.join(sets.GFS_BAS_DIR,'GFS/',today.strftime(format='%Y%m%d'))
            gfs_dir_an = os.path.join(sets.GFS_BAS_DIR, 'GFS/')
            haveGfsFore = oper_tools.check_meteo(gfs_dir_fore, today+timedelta(days=9))
            haveGfsAn = oper_tools.check_meteo(gfs_dir_an, today)
            haveGfs = haveGfsFore and haveGfsAn
            if not haveGfs:
                getGFS(today)
                # сделать bas из tifов GFS
                gfsProc(today)
            haveGfsFore = oper_tools.check_meteo(gfs_dir_fore, today+timedelta(days=9))
            haveGfsAn = oper_tools.check_meteo(gfs_dir_an, today)
            haveGfs = haveGfsFore and haveGfsAn
            result = haveGfs
    else:
        print(f'nothing to do with source={src}')

