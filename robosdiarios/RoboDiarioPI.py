from datetime import datetime, timedelta, date
import traceback

from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.FileManager import DiarioNaoDisponivel
from util.ConfigManager import ConfigManager
import requests
import urllib
from bs4 import BeautifulSoup as bs

class RoboDiarioPI(RoboDiarioBase):
    def __init__(self):
        self.__urldiarios_antigos = "http://www.tjpi.jus.br/site/uploads/diario/dj{data}.pdf"
        self.__urldiarios_novos = "http://www.tjpi.jus.br/site/uploads/diario/dj{data}_{numero}.pdf"
        self.__url_busca_diarios = "http://www.tjpi.jus.br/site/modules/diario/Init.find.mtw?pNum={pagina}&dataInicio=10/08/2006&dataFim={dia:02d}/{mes:02d}/{ano}&conteudoA=diario&conteudoB=&conectivo=and&comConectivo="

        super(RoboDiarioPI, self).__init__("DJPI", "log_robo_pi.txt", "erro_robo_pi.txt")

    def download_atualizacao_diaria(self):

        data_inicial = self.data_inicial("DJPI")
        diarios_a_baixar = self.lista_diarios_faltantes(data_inicial)

        while diarios_a_baixar:
            diario = diarios_a_baixar.pop(0)
            if('Nº' in diario):
                data,numero = diario.split(' - Nº')
                data = datetime.strptime(data,'%d/%m/%Y').date()
                url = self.__urldiarios_novos.format(data=data.strftime("%y%m%d"), numero=numero.strip())
            else:
                data = datetime.strptime(diario,'%d/%m/%Y').date()
                url = self.__urldiarios_antigos.format(data=data.strftime("%y%m%d"))

            name = "DJPI_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))

            conseguiu = False
            self.tentativas = 0

            while not conseguiu:
                try:
                    self.filemanager.download(name, data, url)
                    conseguiu = True
                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    conseguiu = True
                except Exception as e:
                    ConfigManager().escreve_log("Erro: " + traceback.format_exc(e), self.robo, self.erro)
                    self.tentativas += 1

    def lista_diarios_faltantes(self,data_inicial):
        res = requests.get(self.__url_busca_diarios.format(pagina=1,dia=datetime.today().day,mes=datetime.today().month,ano=datetime.today().year))
        html = res.content
        soup = bs(html,"html5lib")
        arquivos_faltantes = []
        encontrou_arquivo_inicial = False
        ultima_pagina = soup.find('div',{'class' : 'paginator'}).find_all('a')[-2].get_text() #se mudar a posição de quem é a última página pode dar erro aqui
        for pagina in range(1,int(ultima_pagina) + 2):
            for tr in soup.find('table').find('tbody').find_all('tr'):
                link_diario = tr.find('td').find('a')
                if link_diario:
                    data_numero_diario = link_diario.get_text().strip()
                    data = data_numero_diario.split(' - Nº')[0]
                    data = datetime.strptime(data,'%d/%m/%Y').date()
                    if data > data_inicial:
                        arquivos_faltantes.insert(0,data_numero_diario.strip())
                    else:
                        if self.data_inicial("DJPI") == self.data_limite(): #significa que ele deve baixar pq a data inicial vem do site, pois não temos diário no banco
                            arquivos_faltantes.insert(0,data_numero_diario.strip())
                        encontrou_arquivo_inicial = True
                        break
            if encontrou_arquivo_inicial:
                break
            res = requests.get(self.__url_busca_diarios.format(pagina=pagina,dia=datetime.today().day,mes=datetime.today().month,ano=datetime.today().year))
            html = res.content
            soup = bs(html,"html5lib")
        return arquivos_faltantes

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioPI()
    robo.download_atualizacao_diaria()