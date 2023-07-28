# DEPRECATED
# ROBOS DEVEM SER CHAMADOS INDIVIDUALMENTE
# BJSMEDELETA
#
# from contextlib import closing
# from datetime import datetime, date, timedelta
# import calendar
# import mimetypes
# import os, sys, shutil
# import traceback
# from PyPDF2.pdf import PdfFileReader
# import requests
# import re
# import urllib
# import time
# from bs4 import BeautifulSoup as bs
# from selenium.webdriver import FirefoxProfile, Firefox, DesiredCapabilities
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import *
# from robosdiarios.RoboDiarioBase import RoboDiarioBase
# from robosdiarios.RoboDiarioTRF1 import RoboDiarioTRF1
# # from robosdiarios.RoboDiarioTRF2 import RoboDiarioTRF2
# # from robosdiarios.RoboDiarioTRF3 import RoboDiarioTRF3
# # from robosdiarios.RoboDiarioTRF4 import RoboDiarioTRF4
# # from robosdiarios.RoboDiarioTRF5 import RoboDiarioTRF5
# from util.StringUtil import remove_acentos, remove_varios_espacos
# from util.ConfigManager import ConfigManager
# from util.FileManager import DiarioNaoDisponivel
# from pdjus.conexao.Conexao import default_schema
# import locale
# import codecs
# from util.DateUtil import parse_mes_para_num
# from util.DateUtil import daterange
# from util.MultiprocessWorkManager import WorkManager, DownloadTask, MergeTask
#
#
# # def myfunction(a, name, data, link, pdfs):
# #    if a.filemanager.download(name, data, link):
# #        pdfs.append(os.path.join(a.filemanager.caminho(name, data), name))
#
# class RoboDiarioTRF (RoboDiarioBase):
#     def __init__(self):
#         self.__url_trf1 = "https://edj.trf1.jus.br/edj/discover?rpp=10&etal=0&scope=123/471&group_by=none&page={pagina}&sort_by=2&order=DESC&filtertype_0=dateIssued&filtertype_1=title&filter_relational_operator_1=contains&filter_relational_operator_0=equals&filter_1=&filter_0={data}"
#         self.__url_trf2 = "http://dje.trf2.jus.br/DJE/Paginas/Externas/inicial.aspx"
#         self.__url_trf3 = "http://web.trf3.jus.br/diario/Consulta/PublicacoesAnteriores/{data}"
#         self.__url_trf4 = "https://www2.trf4.jus.br/trf4/diario/edicoes_anteriores.php"
#         self.__url_trf5 = "https://www4.trf5.jus.br/diarioeletinternet/index.jsp"
#         # self.__url_trf5 = "https://www.trf5.jus.br/diarioeletinternet/paginas/consultas/consultaDiario.faces"
#         self.__url_atas_distrib_trf3 = "http://web.trf3.jus.br/atasdistribuicao/Ata/ListarDados/{}"
#         super (RoboDiarioTRF, self).__init__ ("TRF", "TRF_robodiario.txt", "TRF_robodiario.err")
#
#     def download_atualizacao_diaria(self):
#
#         #self._donwload_atas_distribuicao_trf3()
#
#         self.__download_trf1()
#         # self.__download_trf2()
#         # self.__download_trf3()
#         # self.__download_trf4()
#         # self.__download_trf5()
#
#         # self.__download_trf1_imprensanacional() # 05/10/2009 a 12/2014
#         # self.__download_trf1_antigo() # pre 05/10/2009
#
#     def get_header(self, s, form=None):
#         headers = {
#             "Host": "www.trf5.jus.br",
#             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#             "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
#             "Accept-Encoding": "gzip, deflate",
#             "DNT": 1,
#             "Content-Type": "text/html;charset=ISO-8859-1",
#             "Referer": "https://www.trf5.jus.br/diarioeletinternet/index.jsp",
#             "Content-Length": 348,
#             "Cookie": "JSESSIONID=0FCB6409881F112D6255F848209C82CB",
#             "Connection": "keep-alive",
#             "Pragma": "no-cache",
#             "Cache-Control": "no-cache",
#         }
#         if form:
#             headers["Content-Type"] = "application/x-www-form-urlencoded"
#             headers["Content-Length"] = len (urllib.parse.urlencode (form))
#
#         return headers
#
#
#     def __download_trf1(self):
#
#         ConfigManager ().escreve_log ("TRF 1ª região...", self.robo, self.log)
#
#         RoboTRF1 = RoboDiarioTRF1()
#         RoboTRF1.download_trf1 ()
#
#
#     def __download_trf2(self):
#
#         ConfigManager ().escreve_log ("TRF 2ª região...", self.robo, self.log)
#
#         RoboTRF2 = RoboDiarioTRF2 ()
#
#         RoboTRF2.retry_failed_downloads (self.robo, self.log, self.erro)
#
#         for i in range (RoboTRF2.check_last_downloaded_file (), RoboTRF2.check_last_downloaded_file () + 20000):
#             RoboTRF2.process (i, self.robo, self.log, self.erro)
#
#
#     def __download_trf3(self):
#
#         RoboTRF3 = RoboDiarioTRF3()
#
#         RoboTRF3.download_trf3 ()
#         RoboTRF3.download_atualizacao_diaria()
#
#     def __download_trf4(self):
#
#         RoboTRF4 = RoboDiarioTRF4()
#
#         RoboTRF4.download_trf4 ()
#         RoboTRF4.download_atualizacao_diaria ()
#
#     def __download_trf5(self):
#
#         RoboTRF5 = RoboDiarioTRF5()
#
#         RoboTRF5.download_trf5()
#         RoboTRF5.download_atualizacao_diaria ()
#
#
#     def isFullFile(self, file_path):
#         return os.path.isfile (file_path) and os.path.getsize (file_path) > 0
#
#
#     def move_arquivos_subfolders(self, pasta, subfolders):
#         arquivos = os.listdir (pasta)
#         for arquivo in arquivos:
#             try:
#                 # print(os.path.join(pasta, arquivo))
#                 # print(os.path.abspath(self.filemanager.caminho(arquivo, self.filemanager.obter_data(arquivo),subfolders=subfolders)))
#                 shutil.move (os.path.join (pasta, arquivo), os.path.abspath (
#                     self.filemanager.caminho (arquivo, self.filemanager.obter_data (arquivo), subfolders=subfolders)))
#             except Exception as e:
#                 pass
#
#
#     def esvazia_pasta(self, path_pasta):
#         for file in os.listdir (path_pasta):
#             file_path = os.path.join (path_pasta, file)
#             try:
#                 if os.path.isfile (file_path):
#                     os.unlink (file_path)
#                     # elif os.path.isdir(file_path): shutil.rmtree(file_path)
#             except Exception as e:
#                 print (e)
#
#
#     def escreve_log(self, txt):
#         ConfigManager ().escreve_log (txt, self.robo, self.log, verbose=False)
#
#
#     def move_arquivos(self, pasta):
#         arquivos = os.listdir (pasta)
#         for arquivo in arquivos:
#             nome = self.novo_nome (arquivo)
#             if nome:
#                 try:
#                     os.rename (os.path.join (pasta, arquivo), os.path.join (
#                         self.filemanager.caminho (arquivo, self.filemanager.obter_data (arquivo)), nome))
#                 except Exception as e:
#                     pass
#
#     def novo_nome(self, antigo):
#         if not "TRF2" in antigo or ".part" in antigo:
#             return None
#         regex = re.search ("(\d{2}\d{2}\d{4})_.*_(.*)\.(.*)", antigo)
#         data = datetime.strptime (regex.group (1), "%d%m%Y").date ()
#         caderno = regex.group (2)
#         extensao = regex.group (3)
#         if data and caderno and extensao:
#             novo = "TRF02_" + caderno + "_" + data.strftime ("%Y_%m_%d") + "." + extensao
#         else:
#             novo = None
#         return novo
#
#     def __add_months(self, sourcedate, months):
#         month = sourcedate.month - 1 + months
#         year = int (sourcedate.year + month // 12)
#         month = month % 12 + 1
#         day = min (sourcedate.day, calendar.monthrange (year, month)[1])
#         return date (year, month, day)
#
#     def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True, somente_inicio_mes=False, subfolders=None):
#
#         data = super (RoboDiarioTRF, self).data_inicial (filtro, tipo_arquivo, por_tipo, subfolders)
#
#         if somente_inicio_mes:
#             return data.replace (day=1)
#
#         return data
#
#     def data_limite(self):
#         return date (2006, 10, 1)
#
#
# if __name__ == '__main__':
#     robo = RoboDiarioTRF()
#     robo.download_atualizacao_diaria()
