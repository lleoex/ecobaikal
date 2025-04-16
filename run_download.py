import os.path
from os import listdir

from datetime import datetime
import sys
import argparse
import ecobaikal_shortterm
#from EE_export import getEra, getGFS
from era2bas import eraProc
from gfs2bas import gfsProc
from receiver import receivemail
from oper_tools import makeHydr
from settings import Settings


workdir = ""
sets = Settings()
def getQEnPlusApi(dt:datetime):
    #receivemail()
    files = [f for f in listdir(sets.EMAIL_XLS_DIR) if (os.path.isfile(os.path.join(sets.EMAIL_XLS_DIR, f)) and dt.strftime('%Y%m%d') in f)]
    makeHydr(os.path.join(sets.EMAIL_XLS_DIR,files[0]))

def checkQEnPlus(dt:datetime) -> bool:
    flag_path = os.path.join(workdir,dt.strftime('%Y%m%d'),'qflag.txt')
    if not os.path.exists(flag_path):
        #getQEnPlusApi(dt)
        checkQEnPlus(dt)
    return True

def checkEra(dt:datetime) -> bool:
    return False

def checkGfs(dt:datetime) -> bool:
    #ищем в два этапа. от Д-8 до Д, и от Д до Д+10
    return False

def checkEmg(dt:datetime) -> bool:
    """
    Return true if it is necessary to run Emg (does not exist result file)
    :param dt:
    :return:
    """
    return False
def checkData(dt:datetime) -> bool:
    """

    :param dt:
    :return: True if it needs to run emg. False if already done or not enough data
    """
    return checkEmg(dt) and checkQEnPlus(dt) and checkEra(dt) and checkGfs(dt)



if __name__ == '__main__':
    # today =  datetime.date.today()
    parser = argparse.ArgumentParser(description='downloader')
    parser.add_argument('--date_today', type=str, help='Дата начала расчета гггг-мм-дд', required=True)
    parser.add_argument('--source', choices=['Q', 'GFS', 'ERA'], required=True)

    args = parser.parse_args()

    src = args.source
    today = datetime.strptime(args.date_today,'%Y-%m-%d')
    if src == "Q":
        getQEnPlusApi(today)
    elif src == "ERA":
        #getEra(today)
        print("ERA")
    elif src == "GFS":
        #getGFS(today)
        print("GFS")
    else:
        print(f'nothing to do with source={src}')