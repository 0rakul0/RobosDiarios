# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import re
import traceback
import requests
import dateparser
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from bs4 import BeautifulSoup as bs


class RoboDiarioBA(RoboDiarioBase):

    def __init__(self):
        self.__urldiarios = "https://diario.tjba.jus.br/diario/internet/download.wsp?tmp.diario.nu_edicao={edicao}&tmp.diario.cd_caderno=&tmp.diario.cd_secao=&tmp.diario.dt_inicio=11/10/2018&tmp.diario.dt_fim=24/10/2018&tmp.diario.id_advogado=&tmp.diario.pal_chave="
        super(RoboDiarioBA, self).__init__("DJBA", "log_robo_ba.txt", "erro_robo_ba.txt")

    def download_atualizacao_diaria(self):
        #requests.packages.urllib3.disable_warnings()

        atual = datetime.now().date()


        conseguiu = False
        self.tentativas = 0

        while not conseguiu:
            try:
                s = requests.Session()
                url = "https://diario.tjba.jus.br/diario/internet/pesquisar.wsp"
                pagina = s.get(url)
                soup = bs(pagina.text, "html5lib")
                token = soup.find("input",{"id":"wi.token"})["value"]

                data = self.data_inicial("DJBA")

                params = {'tmp.diario.dt_inicio': data.strftime("%d/%m/%Y"), 'tmp.diario.dt_fim': atual.strftime("%d/%m/%Y"),'wi.token':token}



                pagina = s.post(url, data=params, verify=False,timeout=self.timeout)

                soup = bs(pagina.text, "html5lib")
                tbl_diarios = soup.find_all("table", {"class": "grid"})[0]

                if tbl_diarios:
                    for td in tbl_diarios.find_all("td",{"class": "grid_center"})[::-1]:
                            if td.text.strip():
                                link = td.find("a")
                                id = re.search('Edi..o.*?(\d+)', link.text)
                                data = link.find("b").text
                                dt = dateparser.parse(data)

                                params = {'tmp.diario.nu_edicao' : id.group(1)}
                                self.__urldiarios.format(edicao = params)
                                name = "DJBA_{data}.pdf".format(data=dt.strftime("%Y_%m_%d"))

                                try:

                                    if self.filemanager.download(name, dt, self.__urldiarios):
                                        print ('Processo', name, ' salvo com sucesso')
                                    else:
                                        print('Diário', name, ' não baixado')
                                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    conseguiu = True
            except Exception as e:
                ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)
                self.tentativas += 1





    def data_limite(self):
        return date(2009,5,13)


if __name__ == '__main__':
    robo = RoboDiarioBA()
    robo.download_atualizacao_diaria()