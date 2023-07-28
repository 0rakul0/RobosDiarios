from datetime import datetime, timedelta, date
import os
import re
import requests
import time
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.FileManager import DiarioNaoDisponivel, MaxTentativasExcedidas
from util.ConfigManager import ConfigManager
from bs4 import BeautifulSoup

class RoboDiarioDF(RoboDiarioBase):

    def __init__(self):
        self.__urldiarios = "https://dje.tjdft.jus.br/dje/djeletronico"
        super(RoboDiarioDF, self).__init__("DJDF", "log_robo_df.txt", "erro_robo_df.txt")


    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial("DJDF")

        while atual >= data:
            name = "DJDF_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))

            try:
                params = {'visaoId':'tjdf.djeletronico.comum.internet.apresentacao.VisaoDiarioEletronicoInternetPorData',
                        'controladorId':'tjdf.djeletronico.comum.internet.apresentacao.ControladorDiarioEletronicoInternetPorData',
                        'idDoUsuarioDaSessao':'',
                        'nomeDaPagina':'dados',
                        'comando':'consultarDiariosDaData',
                        'enderecoDoServlet':'djeletronico',
                        'visaoAnterior':'tjdf.djeletronico.comum.internet.apresentacao.VisaoDiarioEletronicoInternetPorData',
                        'skin':'',
                        'tokenDePaginacao':3,
                        'idDoDiarioSelecionado':'',
                        'internet':1,
                        'data': data.strftime("%d/%m/%Y")}


                try:
                    pagina = requests.post(self.__urldiarios, data=params, verify=False, timeout=5)
                    requests.session().close()
                except Exception as e:
                    break
                # if pagina.status_code != 200:
                #     break

                match = re.search('<table.*id="tabela_diariosConsultados".*<\/table>',pagina.text,re.I)
                if match:
                    soup = match.group(0)
                    root = BeautifulSoup(soup,'html5lib')
                    link = root.findAll('a',{"target": "_blank"})[0]
                    url = link['href']

                    self.filemanager.download(name, data,url)
            except (DiarioNaoDisponivel, FileNotFoundError) as e:
                ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                    data=data.strftime("%d/%m/%Y")), self.robo, self.log)

            data += timedelta(1)

    def download_antigos(self):
        url = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={caderno}&pagina={page}&data={data}&captchafield=firistAccess"

        # data = date(1990, 1, 2)
        # atual = datetime.now().date()
        atual = self.data_limite()
        for caderno in (4,5,6):
            # data = date(1990, 1, 2)
            data = self.data_inicial("DJDF_Caderno{caderno}".format(caderno=caderno))
            while atual >= data:
                try:
                    ConfigManager().escreve_log("Acessando diário do caderno {caderno} de {data}".format(caderno=caderno,data=data.strftime("%d/%m/%Y")),
                                            self.robo, self.log)
                    name = "DJDF_Caderno_{caderno}_{data}.pdf".format(caderno=caderno,data=data.strftime("%Y_%m_%d"))
                    pdfs = self.get_todas_paginas(url,caderno,data)

                    final = os.path.join(self.filemanager.caminho(name, data, True), name)
                    self.filemanager.juntar_pdfs(final, pdfs,apagar_arquivos=True)
                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                data += timedelta(1)

    def get_todas_paginas(self, url,caderno,data):
        pdfs = []
        pagina = 1
        pdf = self.get_pagina(url,caderno,data, pagina)
        if os.path.isfile(pdf) and not pdf in pdfs:
            pdfs.append(pdf)
        pagina += 1
            #Eu gostaria de ter feito while True. (Torok 2016) afirma que é melhor replicar código. Odeie ele.
            #Torok aqui. Culpe o Guido Von Rossum por achar que do-while era bobagem.
        while os.path.isfile(pdf):
            pdf = self.get_pagina(url,caderno,data, pagina)
            if os.path.isfile(pdf) and not pdf in pdfs:
                pdfs.append(pdf)
            pagina += 1
        return pdfs

    def get_pagina(self,url,caderno,data,pagina):
        try:
            name = "DJDF_Caderno{caderno}_{data}_{page:04d}.pdf".format(caderno=caderno,data=data.strftime("%Y_%m_%d"), page=pagina)
            self.filemanager.download(name, data, url.format(caderno=caderno, data=data.strftime("%d/%m/%Y"), page=pagina))
            return os.path.join(self.filemanager.caminho(name, data, True), name)
        except MaxTentativasExcedidas as e:
            if "Diário não disponível na data solicitada." in str(e): # Este diario baixa até não ter mais páginas e dar erro 404
                return None
            raise e
        except (DiarioNaoDisponivel, FileNotFoundError) as e:
            return None

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioDF()
    # robo.download_antigos()
    atual = datetime.now ().date ()
    data = robo.data_inicial('DJDF')
    while atual > data:
        robo.download_atualizacao_diaria()

    print ('FOI!!')
