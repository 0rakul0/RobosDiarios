# =============================================================================
# Pacote para adicionar minha pasta local no PYTHONPATH para testar o módulo
# localmente. Deletar antes do push.
# =============================================================================
#import site
#site.addsitedir("C:\\Users\\b2552833\\Documents\\IpeaJUS")
# =============================================================================
# Fim dos pacotes locais
# =============================================================================

import multiprocessing
import os
import sys

from pdjus.conexao.Conexao import Singleton
from util.ConfigManager import ConfigManager



class SharedVars(metaclass=Singleton):

    def __init__(self):

        ConfigManagerTRF2 = ConfigManager()
        
        self.pathLogs = ConfigManagerTRF2.le_config("logs")
        self.pathTRF2 = ConfigManagerTRF2.le_config("TRF02")
            
        if not os.path.isdir(self.pathLogs):
            os.makedirs(self.pathLogs)
        if not os.path.isdir(self.pathTRF2):
            os.makedirs(self.pathTRF2)
               
# =============================================================================
#     Linux local
# =============================================================================
        
        if sys.platform == "linux":
    
            if not os.path.isdir(self.pathTRF2 + "/pdf"):
                os.makedirs(self.pathTRF2 + "/pdf")
            if not os.path.isdir(self.pathTRF2 + "/tmp"):
                os.makedirs(self.pathTRF2 + "/tmp")

            self.url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
            self.basedir_files = self.pathTRF2 + "/pdf"
            self.tempdir_files = self.pathTRF2 + "/tmp"
            self.log_files = self.pathTRF2 + "/log.pickle"
            self.log_failed_downloads = self.pathTRF2 + "/failed_download_log.pickle"


# =============================================================================
#     Windows local
# =============================================================================
# =============================================================================
    
        if sys.platform == "win32":
            
            if not os.path.isdir(self.pathTRF2 + "\\pdf"):
                os.makedirs(self.pathTRF2 + "\\pdf")
            if not os.path.isdir(self.pathTRF2 + "\\tmp"):
                os.makedirs(self.pathTRF2 + "\\tmp")
             
            self.url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
            self.basedir_files = self.pathTRF2 + "\\pdf"
            self.tempdir_files = self.pathTRF2 + "\\tmp"
            self.log_files = self.pathTRF2 + "\\log.pickle"
            self.log_failed_downloads = self.pathTRF2 + "\\failed_download_log.pickle"
        
# =============================================================================
# =============================================================================
#     Linux servidor: dm-new
# =============================================================================
        
#        if sys.platform == "linux":
#            
#            if not os.path.isdir(self.pathTRF2 + "/pdf"):
#                os.makedirs(self.pathTRF2 + "/pdf")
#            if not os.path.isdir(self.pathTRF2 + "/tmp"):
#                os.makedirs(self.pathTRF2 + "/tmp")
#            
#            self.url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
#            self.basedir_files = "/mnt/dmlocal/dados/TRF/TRF02/pdf"
#            self.tempdir_files = "/mnt/dmlocal/dados/TRF/TRF02/tmp"
#            self.log_files = "/mnt/dmlocal/dados/TRF/TRF02/log.pickle"
#            self.log_failed_downloads = "/mnt/dmlocal/dados/TRF/TRF02/failed_downloads_log.pickle"
    
