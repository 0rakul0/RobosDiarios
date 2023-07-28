# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import re

class RoboDiarioAC(RoboDiarioBase):

    def __init__(self):
        self.sessao = requests.Session ()
        self.url_base = 'https://diario.tjac.jus.br'
        self.url = "https://diario.tjac.jus.br/edicoes.php?Ano={ANO}&Mes={MES}"
        # self.__url_json = "http://esaj.tjce.jus.br/cdje/getListaDeCadernos.do?dtDiario={DATE}"
        # self.__url_download = "http://esaj.tjce.jus.br/cdje/downloadCaderno.do?dtDiario={DATE}&cdCaderno={CAD}"
        super(RoboDiarioAC, self).__init__("DJAC", "log_robo_ac.txt", "erro_robo_ac.txt")

    def download_atualizacao_diaria_2023(self):
        atual = datetime.now().date()

        data = self.data_inicial('DJAC')
        # data = date(2001,6,1)
        op = Options()
        # op.add_argument('--headless')  # para abrir o navegador comentar essa linha

        driver = webdriver.Chrome(executable_path=r'../chrome/chromedriver', options=op)
        driver.set_window_size(480,320)
        dict_meses = {'janeiro': '1', 'fevereiro': '2', 'marco': '3', 'abril': '4', 'maio': '5', 'junho': '6',
                      'julho': '7', 'agosto': '8',
                      'setembro': '9', 'outubro': '10', 'novembro': '11', 'dezembro': '12'}
        while atual >= data:
            conseguiu = False
            self.tentativas = 0

            while not conseguiu:
                try:
                    url = self.url.format(ANO=data.year, MES=data.month)
                    time.sleep(1)
                    driver.get(url)
                    time.sleep(1)
                    soup = bs(driver.page_source, 'html.parser')
                    diarios = soup.find_all('a', {'title': 'Baixar'})

                    if len(diarios) is 0:
                        conseguiu = True

                    self.escreve_log("Acessando diário em {}".format(url))

                    for diario in enumerate(diarios):
                        url_download = self.url_base + diario[1].attrs['href']
                        data_diario = diario[1].parent.parent.text
                        data_diario = remove_quebras_linha_de_linha(remove_varios_espacos(data_diario.replace
                                                                                          ('\n', '').replace('\t',
                                                                                                             '').replace(
                            'de ', ''))).replace(' ', '/').replace('Ã§', 'c')
                        lista_data = data_diario.split('/')
                        mes = re.search('\/(.*)\/', data_diario).group(1)
                        mes = re.sub('\/(.*)\/', mes, dict_meses[mes])
                        data_diario = date(int(lista_data[2]), int(mes), int(lista_data[0]))
                        name = "DJAC_{data}.pdf".format(data=data_diario.strftime("%Y_%m_%d"))
                        self.filemanager.download(name, data=data_diario, url=url_download)
                        conseguiu = True
                    self.escreve_log(
                        'Sem mais diários disponíveis para download no dia {}!!!'.format(str(data.strftime('%Y-%m'))))

                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    conseguiu = True
                except Exception as e:
                    ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)
                    self.tentativas += 1

            data = data.replace(day=1)
            data += timedelta(32)
            data = data.replace(day=1)

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial('DJAC')
        # data = date(2001,6,1)

        dict_meses = {'janeiro': '1', 'fevereiro': '2', 'marco': '3', 'abril': '4', 'maio':'5','junho':'6','julho':'7', 'agosto':'8',
                      'setembro':'9','outubro':'10','novembro':'11', 'dezembro':'12'}
        while atual >= data:
            conseguiu = False
            self.tentativas = 0

            while not conseguiu:
                try:
                    url = self.url.format(ANO=data.year, MES=data.month)
                    pagina = requests.get(url)
                    soup = bs(pagina.content, 'html5lib')
                    diarios = soup.find_all('a', {'title':'Baixar'})

                    if len(diarios) is 0:
                        conseguiu = True

                    self.escreve_log("Acessando diário em {}".format(url))

                    for diario in enumerate(diarios):
                        url_download = self.url_base + diario[1].attrs['href']
                        data_diario = diario[1].parent.parent.text

                        data_diario = remove_quebras_linha_de_linha(remove_varios_espacos(data_diario.replace
                                                                                          ('\n','').replace('\t','').replace('de ',''))).replace(' ','/').replace('ç','c')
                        lista_data = data_diario.split('/')
                        mes = re.search ('\/(.*)\/', data_diario).group(1)
                        mes = re.sub ('\/(.*)\/', mes, dict_meses[mes])
                        data_diario = date(int(lista_data[2]), int(mes), int(lista_data[0]))
                        name = "DJAC_{data}.pdf".format (data=data_diario.strftime ("%Y_%m_%d"))
                        self.filemanager.download (name, data=data_diario, url=url_download)
                        conseguiu = True
                    self.escreve_log('Sem mais diários disponíveis para download no dia {}!!!'.format(str(data.strftime('%Y-%m'))))

                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    conseguiu = True
                except Exception as e:
                    ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)
                    self.tentativas += 1

            data = data.replace(day=1)
            data += timedelta(32)
            data = data.replace(day=1)

    def data_limite(self):
        return date(2023, 7, 20)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioAC()
    robo.escreve_log('########### INÍCIO ROBÔ DJAC ###########')
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJAC #############')
