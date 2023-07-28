# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel

class RoboDiarioMS(RoboDiarioBase):

    def __init__(self):
        self.__url_download = "http://esaj.tjms.jus.br/cdje/downloadCaderno.do?dtDiario={DATA}&cdCaderno={CADERNO}"
        super(RoboDiarioMS, self).__init__("DJMS", "log_robo_ms.txt", "erro_robo_ms.txt")

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        for num_caderno in (1,2,3,4):
            if num_caderno == 1:
                tipo = 'Administrativo'
            elif num_caderno == 2:
                tipo = 'Judicial_2ª_Intancia'
            elif num_caderno == 3:
                tipo = 'Judicial_1ª_Intancia'
            else:
                tipo = 'Editais'

            data = self.data_inicial("DJMS_Caderno{}".format(tipo))

            while atual >= data:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        nome_caderno = "DJMS_Caderno_{tipo}_{data}.pdf".format(tipo=tipo,data=data.strftime("%Y_%m_%d"))
                        url = self.__url_download.format(DATA=data.strftime("%d/%m/%Y"), CADERNO=num_caderno)
                        ConfigManager().escreve_log('['+datetime.now().strftime("%Y-%m-%d %H:%M")+']',"## Acessando diário em {}".format(url), self.robo, self.log)
                        self.filemanager.download(nome_caderno, data, url)
                        conseguiu = True
                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        ConfigManager().escreve_log('['+datetime.now().strftime("%Y-%m-%d %H:%M")+']',"## Diario não disponível na data {data}"
                                                    .format(data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                        conseguiu = True
                    except Exception as e:
                        ConfigManager().escreve_log('['+datetime.now().strftime("%Y-%m-%d %H:%M")+']',"## Erro: {e}".format(e=str(e)), self.robo, self.erro)
                        self.tentativas += 1

                data += timedelta(1)

    def data_limite(self):
        return date(2023, 7, 20)# modificar para a data em que se deseja começar a busca pelos cadernos

if __name__ == '__main__':
    robo = RoboDiarioMS()
    robo.download_atualizacao_diaria()