from datetime import datetime, date
import os
import traceback
import requests
import time
from proxy import Proxy
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
import re



class RoboDiarioRR(RoboDiarioBase):

    def __init__(self):
        self.__url = "http://diario.tjrr.jus.br/dpj/"
        self.__url_download= 'http://diario.tjrr.jus.br/dpj/dpj-{data}.pdf'
        super(RoboDiarioRR, self).__init__("DJRR", "log_robo_rr.txt", "erro_robo_rr.txt")


    def create_proxy(self):

        proxy = Proxy(country_code="BR")
        try:
            ip_port = list(proxy.proxy.items())[0][1].replace('http://', '').split(':')
        except:
            proxy = Proxy()
            ip_port = list(proxy.proxy.items())[0][1].replace('http://', '').split(':')

        addr = [ip_port[0], ip_port[1]]
        proxies = proxy.format_proxy(addr)
        return proxies


    def atualiza_acervo_rr(self):
        conseguiu = False
        s = requests.Session()

        while not conseguiu:
            try:
                url = 'http://diario.tjrr.jus.br/dpj/'
                pagina = s.get(url)
                soup = bs(pagina.text, "html5lib")
                diarios = soup.find_all('a')[5:]

                for diario in diarios:
                    data = self.pega_data(diario)
                    nome = "DJRR_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))
                    link = 'http://diario.tjrr.jus.br/dpj/{}'.format(diario.text)
                    self.escreve_log("Acessando diário em {}".format(link))
                    self.filemanager.download(name=nome,data=data,url=link)
                    conseguiu = True
                conseguiu = True
            except Exception as e:
                self.escreve_log("Erro: {e}".format(e=str(e)))
                self.tentativas += 1

    def download_atualizacao_diaria(self):
        data = self.data_inicial('DJRR')
        s = requests.Session()
        proxies = self.create_proxy()
        s.proxies = proxies
        # data = date(2020,7,19)
        tentativas = 0

        while data <= date.today() and tentativas <= 5:
            try:
                nome = "DJRR_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))
                link = 'http://diario.tjrr.jus.br/dpj/dpj-{}.pdf'.format(str(data).replace('-',''))
                html = s.get(link)

                if html.status_code == 404:
                    self.escreve_log('Caderno não disponível no dia {}'.format(str(data)))
                    # proxies = self.create_proxy()
                    # s.proxies = proxies
                    # tentativas += 1
                    data += relativedelta(days=+1)
                    continue

                self.escreve_log("Acessando diário em {}".format(link))
                baixou, ja_existe = self.filemanager.download(name=nome, data=data, url=link)
                if baixou:
                    tentativas = 0
                    data += relativedelta(days=+1)
                elif not baixou and ja_existe:
                    tentativas = 0
                    data += relativedelta(days=+1)
                else:
                    self.escreve_log('{}. Tentando baixar o caderno DJRR_{} novamente'.format(tentativas, data))
                    tentativas += 1

            except Exception as e:
                self.escreve_log("Erro: {e}".format(e=str(e)))
                self.tentativas += 1


    def pega_data(self, diario):
        data = re.search('\d{8}', diario.text).group(0)
        ano = int(''.join(list(data)[:4]))
        mes = int(''.join(list(data)[4:6]))
        dia = int(''.join(list(data)[6:]))
        data = datetime(day=dia, month=mes, year=ano)
        return data

    def escreve_log(self, texto):
        ConfigManager().escreve_log(texto, self.robo, self.log)


    def data_limite(self):
        return date(2000,1,1)

if __name__ == '__main__':
    robo = RoboDiarioRR()
    #robo.atualiza_acervo_rr()
    robo.download_atualizacao_diaria()