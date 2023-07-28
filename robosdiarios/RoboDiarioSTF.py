from datetime import datetime, timedelta, date

import traceback
from util.FileManager import DiarioNaoDisponivel
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
import requests
from bs4 import BeautifulSoup as bs
import re
from urllib.request import Request, urlopen
class RoboDiarioSTF(RoboDiarioBase):

    def __init__(self):
        self.__urldiarios = "http://www.stf.jus.br/portal/diariojusticaeletronico/montarDiarioEletronico.asp?" \
                            "tp_pesquisa=0&anoDj={ANO}" # "http://dj.stj.jus.br/{data}.pdf"
        self.__urlpdf = "http://redir.stf.jus.br/paginadorpub/paginador.jsp?docTP=DJ&docID={ID}&pgI=1"

        super(RoboDiarioSTF, self).__init__("STF", "log_robo_stf.txt", "erro_robo_stf.txt")


    def download_atualizacao_diaria(self):
        atual = datetime.today().year
        ano = self.data_inicial("STF").year

        while ano <= atual:
            indice = None

            try:
                if not indice:
                    #html = requests.get(self.__urldiarios.format(ANO=ano), timeout=self.timeout).content
                    res = Request(self.__urldiarios.format(ANO=ano))
                    res = urlopen(res)
                    soup = bs(html, "html.parser")

                    if soup:
                        resultadoLista = soup.findAll("table", {"class": "resultadoLista"})[0]

                        indice = {}

                        for tr in resultadoLista.findAll("tr"):
                            tds = tr.findAll("td")

                            if tds:
                                data_diario = datetime.strptime(tds[1].text.strip(), '%d/%m/%Y')
                                url_diario_pag = tds[3].find('a').attrs['href']
                                diario_id = re.sub('&data=.*', '', re.sub('.*seq=', '', url_diario_pag)).strip()

                                indice[data_diario] = diario_id

                        for dia in sorted(indice.keys()):
                            ConfigManager().escreve_log("Baixando o diario do dia {dia}".format(
                                dia=dia.strftime("%d/%m/%Y")), self.robo, self.log)
                            name = "DJSTF_{data}.pdf".format(data=dia.strftime("%Y_%m_%d"))

                            try:
                                self.filemanager.download(name, dia, self.__urlpdf.format(ID=indice[dia]))
                            except DiarioNaoDisponivel as e:
                                ConfigManager().escreve_log("Diário não disponível em {dia}".format(
                                    dia=dia.strftime("%d/%m/%Y")), self.robo, self.log)

                        ano += 1
                    else:
                        raise Exception("Página indisponível.")
            except Exception as e:
                ConfigManager().escreve_log("Erro ao acessar diário: {erro}".format(
                    erro=traceback.format_exc()), self.robo, self.erro)
                self.tentativas += 1




    def data_limite(self):
        return date(2007, 1, 1)

if __name__ == '__main__':
    robo = RoboDiarioSTF()
    robo.download_atualizacao_diaria()