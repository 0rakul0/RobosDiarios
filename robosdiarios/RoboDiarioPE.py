from datetime import timedelta, datetime, date
import traceback

import requests
from bs4 import BeautifulSoup as bs

from util.ConfigManager import ConfigManager
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioPE(RoboDiarioBase):
    def __init__(self):
        #self.__urldiarios = "https://www.tjpe.jus.br/dje/djeletronico?visaoId=tjdf.djeletronico.comum.internet.apresentacao.VisaoDiarioEletronicoInternetPorData&idDoIndice=1_1&idDoUsuarioDaSessao=null"
        self.__urldiarios = "https://www.tjpe.jus.br/dje/djeletronico"

        super(RoboDiarioPE, self).__init__("DJPE", "log_robo_pe.txt", "erro_robo_pe.txt")

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial("DJPE")

        while atual >= data:
            name = None

            conseguiu = False
            self.tentativas = 0

            while not conseguiu:
                try:
                    name = "DJPE_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))

                    ConfigManager().escreve_log("Acessando {}".format(self.__urldiarios), self.robo, self.log)

                    params = {
                        #'comando' : "consultarDiariosDaData" ,


                        "visaoId":"tjdf.djeletronico.comum.internet.apresentacao.VisaoDiarioEletronicoInternetPorData",
                        "controladorId":"tjdf.djeletronico.comum.internet.apresentacao.ControladorDiarioEletronicoInternetPorData",
                        "idDoIndice" : "1_1",
                        "nomeDaPagina":"dados",
                        "comando":"consultarDiariosDaData",
                        "enderecoDoServlet":"djeletronico",
                        "visaoAnterior":"tjdf.djeletronico.comum.internet.apresentacao.VisaoDiarioEletronicoInternetPorData",
                        "tokenDePaginacao":"5",
                        "internet":"1",
                        "diariosConsultados":"id,ano,numero,dataDePublicacaoDoDiario,linkBaixarPDF,linkBaixarP7S",
                        "diariosConsultados_qtd":"1",
                        "diariosConsultados_id_0":"47288",
                        "diariosConsultados_ano_0":str(data.year),
                        "diariosConsultados_numero_0":"65",
                        #"diariosConsultados_dataDePublicacaoDoDiario_0":"2009-05-30 00:00:00.0",
                        "diariosConsultados_dataDePublicacaoDoDiario_0": data.strftime("%Y-%m-%d") + " 00:00:00.0",
                        "diariosConsultados_linkBaixarPDF_0":"<a href = 'http://www.tjpe.jus.br/dje/DownloadServlet?dj=DJ65_2015-ASSINADO.PDF&statusDoDiario=ASSINADO' class='downloadPdf' target='_blank' title='Visualizar Diário'>Visualizar</a>",
                        "diariosConsultados_linkBaixarP7S_0":"<a href = 'http://www.tjpe.jus.br/dje/DownloadServlet?dj=DJ65_2015-ASSINADO.PDF.P7S&statusDoDiario=ASSINADO' class='downloadAssinado' target='_blank' title='Visualizar Diário'>Visualizar</a>",
                        'data': data.strftime("%d/%m/%Y")
                        #"data":"30/05/2009"
                    }
                    pagina = requests.post(self.__urldiarios,data=params, verify=False)

                    result = bs(pagina.text, "html5lib")

                    link = result.find("a",attrs={'class':'downloadPdf'})
                    if link:
                        url = link.attrs['href']
                        ConfigManager().escreve_log("Acessando {}".format(url), self.robo, self.log)
                        try:
                            self.filemanager.download(name, data, url)
                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                            ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                                data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    else:
                        ConfigManager().escreve_log("Não conseguiu achar a criptografia no dia {data}".
                                                    format(data=data.strftime("%Y_%m_%d")), self.robo, self.log)
                    conseguiu = True
                except Exception as e:
                    ConfigManager().escreve_log("Erro "+ name + ":  " + traceback.format_exc(e), self.robo, self.erro)
                    self.tentativas += 1

            data += timedelta(1)

    def data_limite(self):
        return date(2009,5,22)

if __name__ == '__main__':
    robo = RoboDiarioPE()
    robo.download_atualizacao_diaria()
