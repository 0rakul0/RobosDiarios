# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import re
import traceback

import requests

from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioPR(RoboDiarioBase):

    def __init__(self):
        self.__url_crypto = "http://portal.tjpr.jus.br/e-dj/publico/diario/pesquisar.do"
        self.__url_download = "http://portal.tjpr.jus.br/e-dj/publico/diario/baixar.do?tjpr.url.crypto="
        super(RoboDiarioPR, self).__init__("DJPR", "log_robo_pr.txt", "erro_robo_pr.txt")

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial("DJPR")

        while atual >= data:
            conseguiu = False
            self.tentativas = 0

            while not conseguiu:
                try:
                    name = "DJPR_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))

                    self.__url_crypto = 'http://portal.tjpr.jus.br/e-dj/publico/diario/pesquisar.do'
                    ConfigManager().escreve_log("Acessando {}".format(self.__url_crypto), self.robo, self.log)

                    params = {'dataVeiculacao': data.strftime("%d/%m/%Y")}
                    pagina = requests.post(self.__url_crypto, data=params, verify=False, timeout=self.timeout)
                    result = re.search("([c][r][y][p][t][o][=])(.*)(['][])])",pagina.text)
                    if result:
                        crypto = result.group(2)

                        url = self.__url_download + str(crypto)
                        ConfigManager().escreve_log("Acessando {}".format(url), self.robo, self.log)

                        try:
                            self.filemanager.download(name, data, url, False)
                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                            ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                                data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    else:
                        ConfigManager().escreve_log("Não conseguiu achar a criptografia no dia {data}".
                                                    format(data=data.strftime("%Y_%m_%d")), self.robo, self.log)

                    conseguiu = True
                except Exception as e:
                    ConfigManager().escreve_log("Erro: " + str(e), self.robo, self.erro)
                    self.tentativas += 1

            data += timedelta(1)

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioPR()
    robo.download_atualizacao_diaria()