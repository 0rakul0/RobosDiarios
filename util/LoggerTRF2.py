import os
import pickle
import multiprocessing

import util.SharedVarsTRF2 as SharedVars
from pdjus.conexao.Conexao import Singleton

from util.ConfigManager import ConfigManager

    
class Logger(metaclass=Singleton):
    def __init__(self):
        if os.path.isfile(SharedVars.SharedVars().log_files):
            with open(SharedVars.SharedVars().log_files, "rb") as f:
                self.__downloaded = pickle.load(f)
        else:
            self.__downloaded = set()
        if os.path.isfile(SharedVars.SharedVars().log_failed_downloads):
            with open(SharedVars.SharedVars().log_failed_downloads, "rb") as f:
                self.__faileddownloads = pickle.load(f)
        else:
            self.__faileddownloads = set()

    def log(self, id, newfilename, robo, log):
        self.__downloaded.add(id)
        with open(SharedVars.SharedVars().log_files, "wb") as f:
            pickle.dump(self.__downloaded, f)
        ConfigManager().escreve_log("Baixou o diario  {}".format(newfilename), robo, log)
            
    def is_file_downloaded(self, id):
        return id in self.__downloaded
    
# =============================================================================
# Conjunto de métodos para gerar um log dos downloads que falharam e eventualmente
# limpa-los caso eles sejam bem sucedidos
# =============================================================================

    def log_failed(self, id, robo, erro):
        self.__faileddownloads.add(id)
        with open(SharedVars.SharedVars().log_failed_downloads, "wb") as f:
            pickle.dump(self.__faileddownloads, f)
        ConfigManager().escreve_log("Erro no id: {}...".format(id), robo, erro)
            
    def clean_failed_log(self, id):
        self.__faileddownloads.remove(id)
        with open(SharedVars.SharedVars().log_failed_downloads, "wb") as f:
            pickle.dump(self.__faileddownloads, f)
            
    
    def check_failed_downloads(self):
        return self.__faileddownloads
    
    def list_of_failed_downloads(self):
        return list(self.__faileddownloads)