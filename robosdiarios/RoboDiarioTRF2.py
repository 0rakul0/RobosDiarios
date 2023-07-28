import re
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
import os.path


class RoboDiarioTRF2(RoboDiarioBase):
    """
    Robo responsavel pelo download de diarios oficias do TRF2.
    """
    def __init__(self):
        super(RoboDiarioTRF2, self).__init__("TRF02", "TRF2_robodiario.txt", "TRF2_robodiario.err")
        self.url_trf2 = 'http://dje.trf2.jus.br/DJE/Paginas/Externas/inicial.aspx'
        self.proxies = {'http': 'cache.ipea.gov.br:3128'}

    def download_atualizacao_diaria(self):
        """
        Aciona o metodo de download de diarios oficiais a partir de uma data definida.
        """
        self.download_trf2()

    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return datetime.date(datetime(2009,11,1))

    def data_de_busca(self, data_inicial):
        """
        Retorna datas dos diarios que devem ser baixados.
        """
        if data_inicial + relativedelta(days=-7) <= self.data_limite():
            data_inicial = self.data_limite()
        else:
            data_inicial = data_inicial + relativedelta(days=-7)

        primeira_data = data_inicial

        while True:
            yield primeira_data
            primeira_data = primeira_data + relativedelta(days=1)
            if primeira_data > datetime.date(datetime.now()):
                yield datetime.date(datetime.now())
                break

    def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True,somente_inicio_mes=False, subfolders=None):
        """
        Retorna a data do ultimo diario baixado.
        """
        data = super(RoboDiarioTRF2, self).data_inicial(filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self, txt):
        ConfigManager ().escreve_log (txt, self.robo, self.log, verbose=False)

    def download_trf2(self):
        """
        Realiza o download dos diarios para as datas definidas.
        """
        self.escreve_log('########### INICIO TRF02 ###########')
        print('########### INICIO TRF02 ###########')

        data_do_ultimo_download = self.data_inicial("TRF2")

        for DataDeBusca in self.data_de_busca(data_do_ultimo_download):

            print("Data de Busca: {:02}/{:02}/{:04}".format(DataDeBusca.day, DataDeBusca.month, DataDeBusca.year))
            print("+-+-+-+-+-+-+-+-+-+")

            primeira_pagina = requests.get(self.url_trf2, verify=False, proxies=self.proxies)

            ASPNET_SessionId = primeira_pagina.cookies['ASP.NET_SessionId']
            cookie = {'ASP.NET_SessionId': ASPNET_SessionId}

            primeira_pagina_soup = bs(primeira_pagina.text, 'html5lib')

            __VIEWSTATE = primeira_pagina_soup.find("input", {"id": "__VIEWSTATE"}).attrs['value']
            __EVENTVALIDATION = primeira_pagina_soup.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']

            parametros_primeiro_post = {"__EVENTARGUMENT": "",
                                        "__EVENTTARGET": "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$tbxDataEdicoes",
                                        "__EVENTVALIDATION": __EVENTVALIDATION,
                                        "__LASTFOCUS": "",
                                        "__VIEWSTATE": __VIEWSTATE,
                                        "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$meeDataInicial_ClientState": "",
                                        "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$OpcaoVisualizacao": "rbtPDF",
                                        "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$tbxDataEdicoes": "{:02}/{:02}/{:04}".format(DataDeBusca.day, DataDeBusca.month, DataDeBusca.year),
                                        "ctl00$ContentPlaceHolder$ctrInicial$OpcaoPesquisa": "rbtDiario",
                                        "ctl00$ScriptManager": "ctl00$ContentPlaceHolder$ctrInicial$upnUpdatePanel|ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$tbxDataEdicoes",
                                        }
            segunda_pagina = requests.post(self.url_trf2, data=parametros_primeiro_post, cookies=cookie, verify=False, proxies=self.proxies)

            segunda_pagina_soup = bs(segunda_pagina.text, 'html5lib')

            links = segunda_pagina_soup.select(".LinkCadernos")

            __VIEWSTATE = segunda_pagina_soup.find("input", {"id": "__VIEWSTATE"}).attrs['value']
            __EVENTVALIDATION = segunda_pagina_soup.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']

            for datalink in links:

                __EVENTTARGET = datalink.attrs['id'].replace('_','$')

                data_arquivo = datetime.strptime("{:02}/{:02}/{:04}".format(DataDeBusca.day,
                                                                            DataDeBusca.month,
                                                                            DataDeBusca.year), "%d/%m/%Y")

                parametros_download_diario = {"__EVENTARGUMENT": "",
                                              "__EVENTTARGET": __EVENTTARGET,
                                              "__EVENTVALIDATION": __EVENTVALIDATION,
                                              "__LASTFOCUS": "",
                                              "__VIEWSTATE": __VIEWSTATE,
                                              "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$tbxDataEdicoes": "{:02}/{:02}/{:04}".format(DataDeBusca.day, DataDeBusca.month, DataDeBusca.year),
                                              "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$meeDataInicial_ClientState": "",
                                              "ctl00$ContentPlaceHolder$ctrInicial$ctrCadernosPorAreaJudicial$OpcaoVisualizacao": "rbtPDF",
                                              "ctl00$ContentPlaceHolder$ctrInicial$OpcaoPesquisa": "rbtDiario"
                                              }

                download_do_diario = requests.post("http://dje.trf2.jus.br/DJE/Paginas/Externas/inicial.aspx",
                                                         cookies=cookie,
                                                         verify=False,
                                                         data=parametros_download_diario,
                                                         files=dict(),
                                                         proxies=self.proxies
                                                         )

                filename = download_do_diario.headers._store['content-disposition'][1]
                filename = re.search('filename=(.*)\.pdf',
                                     download_do_diario.headers._store['content-disposition'][1]).group(1)
                filename = filename.split('_')[1:]
                secao = filename[1]
                caderno = filename[2]

                nome_final_do_arquivo = "TRF02_{CADERNO}_{SECAO}_{DATA}.pdf".format(DATA=data_arquivo.strftime('%Y_%m_%d'),
                                                                       CADERNO=caderno, SECAO=secao)

                with open(self.filemanager.caminho(nome_final_do_arquivo) + os.path.sep + nome_final_do_arquivo, 'wb') as f:
                    f.write(download_do_diario.content)
                    self.escreve_log('Baixou o diário {}'.format(nome_final_do_arquivo))
                    print('Baixou o diário {}'.format(nome_final_do_arquivo))

if __name__ == '__main__':

    robo = RoboDiarioTRF2()
    robo.download_atualizacao_diaria()
    print('########### FIM TRF02 ###########')
