# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
import requests
# disponível de 14 às 8h nos dias úteis e finas de semana 24h por dia

class RoboDiarioAL(RoboDiarioBase):

    def __init__(self):
        self.url = "https://www2.tjal.jus.br/cdje/index.do"
        self.url_download = "http://www2.tjal.jus.br/cdje/downloadCaderno.do?dtDiario={DATE}&cdCaderno={CAD}"
        super(RoboDiarioAL, self).__init__("DJAL", "log_robo_al.txt", "erro_robo_al.txt")


    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        for num_caderno in (2,3):
            if num_caderno == 1:
                tipo = 'Jurisdicional_e_Administrativo'
            else:
                tipo = 'Jurisdicional_Primeiro_Grau'


            data = self.data_inicial('DJAL')
            # data = date(2009,8,1)

            while atual >= data:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        nome_caderno = "DJAL_Caderno_{tipo}_{data}".format(tipo=tipo,data=data.strftime("%Y_%m_%d")).upper()+'.pdf'
                        url = self.url_download.format(DATE=data.strftime("%d/%m/%Y"), CAD=num_caderno)
                        self.escreve_log("Acessando diário em {}".format(url))

                        if 'Não foi possível executar esta operação. Tente novamente mais tarde.' in requests.get(url).text:
                            break

                        self.escreve_log('Baixando caderno {}'.format(nome_caderno))
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
        ConfigManager ().escreve_log ('[' + datetime.now ().strftime ("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo, self.log)

if __name__ == '__main__':
    robo = RoboDiarioAL()
    robo.escreve_log('########### INÍCIO ROBÔ DJAL ###########')
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJAL #############')