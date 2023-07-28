import requests
from bs4 import BeautifulSoup as bs

from pdjus.service.EmpresaService import EmpresaService
from util.CaptchaSolverCadinSP import CaptchaSolverCadinSP
import time
from PIL import Image
from io import BytesIO
import csv

class ConsultaJUCESP():
    def consulta_empresa_por_nire(self,nire):
        self.url = 'https://www.jucesponline.sp.gov.br/'
        s = requests.Session()
