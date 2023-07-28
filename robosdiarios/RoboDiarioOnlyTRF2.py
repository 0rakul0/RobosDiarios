# =============================================================================
# Pacote para adicionar minha pasta local no PYTHONPATH para testar o módulo
# localmente. Atenção ao path onde a pasta IpeaJUS está. Deletar antes do push.
# =============================================================================
#
import site

from pdjus.conexao.Conexao import Singleton

site.addsitedir("C:\\Users\\b2552833\\Documents\\IpeaJUS")

# =============================================================================
# Fim dos pacotes locais
# =============================================================================
import errno
import multiprocessing
import os
import pickle
import random
import re
import shutil
import time
import wget
import socket
import urllib
import sys

import PyPDF2
import requests
from requests.adapters import HTTPAdapter

from urllib3.util.retry import Retry





class SharedVars(metaclass=Singleton):
# =============================================================================
#     Linux local
# =============================================================================
#    url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
#    basedir_files = "/home/DLIPEA/b2552833/TRF2/pdf"
#    tempdir_files = "/home/DLIPEA/b2552833/TRF2/tmp"
#    log_files = "/home/DLIPEA/b2552833/TRF2/log.pickle"
#    log_failed_downloads = "/home/DLIPEA/b2552833/TRF2/failed_download_log.pickle"
# =============================================================================
#     Windows local
# =============================================================================
# =============================================================================
     
     url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
     basedir_files = "C:\\Users\\b2552833\\Documents\\TRF2\\pdf"
     tempdir_files = "C:\\Users\\b2552833\\Documents\\TRF2\\tmp"
     log_files = "C:\\Users\\b2552833\\Documents\\TRF2\\log.pickle"
     log_failed_downloads = "C:\\Users\\b2552833\\Documents\\TRF2\\failed_download_log.pickle"

# =============================================================================
# =============================================================================
#     Linux servidor: dm-new
# =============================================================================
#    
#    url = "http://dje.trf2.jus.br/DJE/Paginas/VisualizarCadernoPDF.aspx?ID={id}"
#    basedir_files = "/mnt/dmlocal/dados/TRF/TRF02/pdf"
#    tempdir_files = "/mnt/dmlocal/dados/TRF/TRF02/tmp"
#    log_files = "/mnt/dmlocal/dados/TRF/TRF02/log.pickle"
#    log_failed_downloads = "/mnt/dmlocal/dados/TRF/TRF02/failed_downloads_log.pickle"

# =============================================================================
# A classe Logger contêm um atributo (neste caso um set object) para guardar
# os valores de Ids que foram baixados pelo programa. A classe contem funções
# para criar um novo arquivo caso ele não exista e escrever neste arquivo
# =============================================================================

class Logger(metaclass=Singleton):
    def __init__(self):
        if os.path.isfile(SharedVars.log_files):
            with open(SharedVars.log_files, "rb") as f:
                self.__downloaded = pickle.load(f)
        else:
            self.__downloaded = set()
        if os.path.isfile(SharedVars.log_failed_downloads):
            with open(SharedVars.log_failed_downloads, "rb") as f:
                self.__faileddownloads = pickle.load(f)
        else:
            self.__faileddownloads = set()

    def log(self, id):
        self.__downloaded.add(id)
        with open(SharedVars.log_files, "wb") as f:
            pickle.dump(self.__downloaded, f)
            
    def is_file_downloaded(self, id):
        return id in self.__downloaded
    
# =============================================================================
# Conjunto de métodos para gerar um log dos downloads que falharam e eventualmente
# limpa-los caso eles sejam bem sucedidos
# =============================================================================

    def log_failed(self, id):
        self.__faileddownloads.add(id)
        with open(SharedVars.log_failed_downloads, "wb") as f:
            pickle.dump(self.__faileddownloads, f)
            
    def clean_failed_log(self, id):
        self.__faileddownloads.remove(id)
        with open(SharedVars.log_failed_downloads, "wb") as f:
            pickle.dump(self.__faileddownloads, f)
            
    
    def check_failed_downloads(self):
        return self.__faileddownloads
    
    def list_of_failed_downloads(self):
        return list(self.__faileddownloads)


def is_downloadable(url):
    session = get_new_session()
    head = session.head(url, allow_redirects=True)
    header = head.headers
    session.close()
    content_type = header.get('content-type')
    return not any(x in content_type.lower() for x in ['text', 'html'])

def get_new_session():
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=1))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# =============================================================================
# get_filename está obtendo o nome errado do arquivo. O header do request
# trás o mesmo nome para diários da mesma região ou seção. João S.(19/02/2018)
# =============================================================================

def get_filename(url):
    session = get_new_session()
    head = session.head(url, allow_redirects=True)
    header = head.headers
    session.close()
    fname = re.findall("filename=(.+)", header.get('content-disposition'))
    return fname[0]

# =============================================================================
# A função download baixa o arquivo presente no id passado. Foi implementado um
# timeout de 60 segundos para evitar que o robo fique preso em um download. O
# motivo para o download congelar ainda não foi determinado
# =============================================================================

def download(url, filename, idx):
    attempts = 0
    while attempts < 2:
        try:
            socket.setdefaulttimeout(60)    
            wget.download(url, out=filename)
            break
        except OSError as e:
            print("\nTempo excedido")
            attempts += 1
            continue
        except KeyboardInterrupt:
            for fileName in os.listdir(SharedVars.tempdir_files):
                os.remove(SharedVars.tempdir_files + "/" + fileName)
            print("\nKeyboardInterrupt")
            sys.exit()			
    else:
        for fileName in os.listdir(SharedVars.tempdir_files):
            os.remove(SharedVars.tempdir_files + "/" + fileName)
        Logger().log_failed(idx)
        print("2 tentativas sem sucesso")
        return 0
    return 1


def move_to_right_directory(temp_filename):
    newfilename, day, month, year = get_info_from_pdf(temp_filename)
    template = "{b}/{y}/{m}"
    directory = template.format(b=SharedVars.basedir_files, y=year, m=month)
    ensure_dir(directory)
    final_file = "{b}/{y}/{m}/{newfilename}".format(
        b=SharedVars.basedir_files, y=year, m=month, newfilename=newfilename
    )
    shutil.move(temp_filename, final_file)


# =============================================================================
# O método process() irá retornar 1 se o download de um determinado id falhou
# =============================================================================

def process(idx):
    url = SharedVars.url.format(id=idx)
    if is_downloadable(url):
        print(" {i} is downloadable!".format(i=idx))
        temp_filename = "{b}/{idx}_{pdf}".format(b=SharedVars.tempdir_files, idx=idx, pdf=get_filename(url))
        if not Logger().is_file_downloaded(idx):
# =============================================================================
# O método download() irá retornar 1 se o download foi bem sucedido e 0 se 
# tiver sido mal sucedido.
# =============================================================================
            if  not download(url, temp_filename, idx):
                return 1
            move_to_right_directory(temp_filename)
            Logger().log(idx)
            time.sleep(random.randint(0, 3))
        else:
            print("{i} is already downloaded".format(i=idx))
    else:
        print("{i} is not downloadable".format(i=idx))


def month2num(month):
    months = {
        'janeiro' : '01', 'fevereiro' : '02', 'mar�o' : '03', 'marco' : '03',
        'abril' : '04', 'maio' : '05', 'junho' : '06', 'julho' : '07', 'agosto' : '08',
        'setembro' : '09', 'outubro' : '10', 'novembro' : '11', 'dezembro' : '12'
    }
    return months[month.lower()]


def extract_data(txt):
    re1 = '((?:(?:[0-2]?\\d{1})|(?:[3][01]{1})))(?![\\d])'  # Day 1
    re2 = '(\\s+)'  # White Space 1
    re3 = '(de)'  # Word 1
    re4 = '(\\s+)'  # White Space 2
    re5 = '((?:[^\W_]+))'  # Word 2
    re6 = '(\\s+)'  # White Space 3
    re7 = '(de)'  # Word 3
    re8 = '(\\s+)'  # White Space 4
    re9 = '((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'  # Year 1
    rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9, re.IGNORECASE | re.DOTALL | re.UNICODE)
    m = rg.search(txt)
    day1 = m.group(1)
    ws1 = m.group(2)
    word1 = m.group(3)
    ws2 = m.group(4)
    month = m.group(5)
    ws3 = m.group(6)
    word3 = m.group(7)
    ws4 = m.group(8)
    year1 = m.group(9)
    return day1, month2num(month), year1

# =============================================================================
# Esta função cria um diretório caso ele não exista e previne certos erros que
# prejudicar o programa. O método usado não previne todos os possíveis erros
# que podem ocorrer ao utilizar o os.makedirs
# =============================================================================

def ensure_dir(full_path):
    try:
        os.makedirs(full_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_pdf_filename(pdf_source_file, day, month, year):
    filename = os.path.basename(pdf_source_file)
    basename = os.path.splitext(filename)[0]
    parts = basename.split('_')
    type, section = parts[-1], parts[-2]
    filename = "TRF02_{t}_{s}_{y}_{m}_{d}.pdf".format(t=type, s=section, y=year, d=day, m=month)
    return filename


def get_info_from_pdf(pdf_file):
    file = open(pdf_file, 'rb')
    ipdf = PyPDF2.PdfFileReader(file)
    pageObj = ipdf.getPage(0)
    rawtxt = pageObj.extractText()
    file.close()
    day,month,year = extract_data(rawtxt)
    newfilename = get_pdf_filename(pdf_file, day, month, year)
    return newfilename, day, month, year

    
# =============================================================================
#  Função para checar o último id baixado e definir o startpoint a partir de 2  
#  ids antes do último. Esta função retorna valores anteriores ao último para
#  assegurar que os DOs foram baixados.
# =============================================================================

def check_last_downloaded_file():
    if os.path.isfile(SharedVars.log_files):
        with open(SharedVars.log_files, "rb") as picklefile:
            logs_id = pickle.load(picklefile)
            startpoint = max(logs_id)
    else:
        startpoint = 1147
    return startpoint - 2

def retry_failed_downloads():
    if Logger().check_failed_downloads():
        for i in Logger().list_of_failed_downloads():
            if not process(i):
                Logger().clean_failed_log(i)

# =============================================================================
#     Função para escrever nos logs que os outros TRFs escrevem.
# =============================================================================
                
# =============================================================================
# A função ConfigManager().escreve_log() já cria automaticamente um log no path
# caso ele não exista. A biblioteca é configurada para fazer alterações no path
# dependendo do SO.
# =============================================================================
                
# =============================================================================
# def write_log_trf(pdf_file):
#     name, day, month, year = get_info_from_pdf(pdf_file)
#     struct_data = time.strptime(day + " " + month + " " + year, "%d %m %Y")
#     path = FileManager.caminho(name, struct_data, subfolders = ["TRF02"])
#     print(path)
# =============================================================================
    
                
if __name__ == "__main__":
    retry_failed_downloads()
    for i in range(check_last_downloaded_file(), 1000000): #range(3478, 1000000):
        process(i)
