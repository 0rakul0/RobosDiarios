# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
import requests
# disponível de 14 às 8h nos dias úteis e finas de semana 24h por dia

class RoboDiarioAM(RoboDiarioBase):

    def __init__(self):
        self.url = "http://esaj.tjam.jus.br/cdje/index.do"
        self.url_json = "http://esaj.tjam.jus.br/cdje/getListaDeCadernos.do?dtDiario={DATE}"
        self.url_download = "http://esaj.tjam.jus.br/cdje/downloadCaderno.do?dtDiario={DATE}&cdCaderno={CAD}"
        # self.url_json = "https://consultasaj.tjam.jus.br/cdje/getListaDeCadernos.do?dtDiario=23%2F01%2F2019"
        super(RoboDiarioAM, self).__init__("DJAM", "log_robo_am.txt", "erro_robo_am.txt")


    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        for num_caderno in (1,2,3,4):
            if num_caderno == 1:
                tipo = 'Administrativo'
            elif num_caderno == 2:
                tipo = 'Judicial_Capital'
            elif num_caderno == 3:
                tipo = 'Judicial_Interior'
            else:
                tipo = 'Distribuicoes_e_Eliminacoes_de_Processos_Judiciais'

            data = self.data_inicial('DJAM')
            # data = date(2016,3,1)

            while atual >= data:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        # params = {'dtDiario': data,
                        #           'cdCaderno': num_caderno}
                        nome_caderno = "DJAM_Caderno_{tipo}_{data}.pdf".format(tipo=tipo,data=data.strftime("%Y_%m_%d"))
                        url = self.url_download.format(DATE=data.strftime("%d/%m/%Y"), CAD=num_caderno)
                        self.escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + ']' + " ## Acessando diário em {}".format(url))
                        # url = requests.post(url, data=params, verify=False, timeout=5)
                        self.filemanager.download(nome_caderno, data, url, tentativas=5)
                        conseguiu = True
                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        self.escreve_log('['+datetime.now().strftime("%Y-%m-%d %H:%M")+']'+" ## Diario não disponível na data {data}"
                                                    .format(data=data.strftime("%d/%m/%Y")))
                        conseguiu = True
                    except Exception as e:
                        self.escreve_log('['+datetime.now().strftime("%Y-%m-%d %H:%M")+']'+" ## Erro: {e}".format(e=str(e)))
                        self.tentativas += 1

                data += timedelta(1)

    def data_limite(self):
        return date(2023, 7, 20) # modificar para a data em que se deseja começar a busca pelos cadernos

    def escreve_log(self, txt):
        ConfigManager().escreve_log(txt, self.robo, self.log)

if __name__ == '__main__':
    robo = RoboDiarioAM()
    robo.escreve_log('########### INÍCIO ROBÔ DJAM ###########')
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJAM #############')