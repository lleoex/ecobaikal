import os
class Settings:
    def __init__(self):
        self.ROOT_DIR = "C:/usr/data/project/en"
        self.ERA_TIFF_DIR = os.path.join(self.ROOT_DIR,"Data/ERA5Land/")
        self.ERA_BAS_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal/Data/Meteo/Eraland/")
        self.GFS_TIFF_DIR = os.path.join(self.ROOT_DIR,"Data/GFS/")
        self.GFS_BAS_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal/Data/Meteo/")
        self.EMG_HYDRO_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal/Data/Hydro/Baikal/")
        self.EMAIL_XLS_DIR = os.path.join(self.ROOT_DIR,"Data/")
        if not os.path.isdir(self.ROOT_DIR):
            self.mkdirs()


    def mkdirs(self):
        if not os.path.isdir(self.ROOT_DIR):
            os.makedirs(self.ROOT_DIR)

        if not os.path.isdir(self.ERA_TIFF_DIR):
            os.makedirs(self.ERA_TIFF_DIR)

        if not os.path.isdir(self.ERA_BAS_DIR):
            os.makedirs(self.ERA_BAS_DIR)

        if not os.path.isdir(self.GFS_TIFF_DIR):
            os.makedirs(self.GFS_TIFF_DIR)

        if not os.path.isdir(self.GFS_BAS_DIR):
            os.makedirs(self.GFS_BAS_DIR)

        if not os.path.isdir(self.EMG_HYDRO_DIR):
            os.makedirs(self.EMG_HYDRO_DIR)

        if not os.path.isdir(self.EMAIL_XLS_DIR):
            os.makedirs(self.EMAIL_XLS_DIR)

'''
def gfsProc(today):
    wd = 'd:/Data/GFS/'
    outDir = 'd:/EcoBaikal/Data/Meteo/'
    
def eraProc():
    # all files in wd
    fromDir = 'D:/Data/ERA5Land/'
    toDir = 'D:/EcoBaikal/Data/Meteo/Eraland/'
    '''



