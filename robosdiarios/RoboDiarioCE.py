# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import traceback
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioCE(RoboDiarioBase):

    def __init__(self):
        self.__url = "http://esaj.tjce.jus.br/cdje/index.do"
        self.__url_json = "http://esaj.tjce.jus.br/cdje/getListaDeCadernos.do?dtDiario={DATE}"
        self.__url_download = "http://esaj.tjce.jus.br/cdje/downloadCaderno.do?dtDiario={DATE}&cdCaderno={CAD}"
        super(RoboDiarioCE, self).__init__("DJCE", "log_robo_ce.txt", "erro_robo_ce.txt")

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        for cad in range(1, 3):
            data = self.data_inicial("DJCE_{tipo}".format(tipo=('administrativo' if cad == 1 else 'justica')))

            while atual >= data:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        name = "DJCE_{tipo}_{data}.pdf".format(data=data.strftime("%Y_%m_%d"),
                                                       tipo=('administrativo' if cad == 1 else 'justica'))
                        url = self.__url_download.format(DATE=data.strftime("%d/%m/%Y"), CAD=cad)
                        ConfigManager().escreve_log("Acessando diário em {}".format(url), self.robo, self.log)

                        self.filemanager.download(name, data, url)
                        conseguiu = True
                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                            data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                        conseguiu = True
                    except Exception as e:
                        ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)
                        self.tentativas += 1

                data += timedelta(1)

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioCE()
    robo.download_atualizacao_diaria()