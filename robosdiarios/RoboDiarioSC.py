# -*- coding: utf-8 -*-


from datetime import datetime, timedelta, date
import os
from proxy import Proxy
import traceback
from util.FileManager import DiarioNaoDisponivel
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.CaptchaSolverESAJ import CaptchaSolverESAJ
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_caracteres_especiais, remove_quebras_linha_de_linha
from util.FileManager import FileManager
from util.ProgressBar import ProgressBar
from bs4 import BeautifulSoup
import time
import pathlib
import requests
from util.ProxyUtil import ProxyUtil
from util.ConfigManager import ConfigManager
import json


class RoboDiarioSC(RoboDiarioBase):

    def __init__(self):
        self.url = "http://busca.tjsc.jus.br/dje-consulta/#/main"
        #self.__urldiarios = "http://busca.tjsc.jus.br/consultadje/visualizadiario.action"
        self.urldiarios = "http://busca.tjsc.jus.br/dje-consulta/rest/diario/caderno?edicao={EDICAO}&cdCaderno={CADERNO}"
        self.url_json = "http://busca.tjsc.jus.br/dje-consulta/rest/busca?q=&pg=1&ps=200&frase=&ou=&not=&dtIni={data}&dtFim={data}"
        self.url_download_text_json = "http://busca.tjsc.jus.br/dje-consulta/rest/busca?q=&pg={pagina}&ps=1&frase=&dtIni={data}&dtFim={data}&cdCaderno={caderno}"
        self.__urlprocessos = "http://esaj.tjsc.jus.br/cpopg/open.do"
        self.__urlprocessosresp = "http://esaj.tjsc.jus.br/cpopg/show.do?conversationId=&" \
                                  "dadosConsulta.localPesquisa.cdLocal={local}&cbPesquisa=NUMPROC&" \
                                  "dadosConsulta.tipoNuProcesso=UNIFICADO&" \
                                  "numeroDigitoAnoUnificado={num_dig_ano}&" \
                                  "foroNumeroUnificado={foro}&dadosConsulta.valorConsultaNuUnificado={npu}&" \
                                  "dadosConsulta.valorConsulta=&vlCaptcha={captcha}"
        self.__urlcaptcha = "http://esaj.tjsc.jus.br/cpopg/imagemCaptcha.do?timestamp={time}"

        super(RoboDiarioSC, self).__init__("DJSC", "log_robo_sc.txt", "erro_robo_sc.txt")


    def create_proxy(self):

        proxy = Proxy(country_code="BR")
        try:
            ip_port = list(proxy.proxy.items())[0][1].replace('http://', '').split(':')
        except:
            proxy = Proxy()
            ip_port = list(proxy.proxy.items())[0][1].replace('http://', '').split(':')

        addr = [ip_port[0], ip_port[1]]
        proxies = proxy.format_proxy(addr)
        return proxies


    def download_atualizacao_diaria(self):

        atual = datetime.now().date()

        data = self.data_inicial("DJSC")

        # data = date(2020,11,1)

        s = requests.Session()

        try:
            s.get(self.url, verify=False, timeout=30)
        except:
            proxies = self.create_proxy()
            s.proxies = proxies
            s.get(self.url, verify=False, timeout=30, proxies=proxies)

        dict_nome_numero_diario = {'Caderno Jurisdicional do Tribunal de Justiça':1, 'Caderno Jurisdicional das Turmas de Recursos e de Uniformização':2, 'Caderno Jurisdicional das Comarcas':3, 'Caderno Administrativo do Poder Judiciário':4}

        while atual >= data:

            dataSemana = data.weekday()

            if dataSemana != 5 and dataSemana != 6:

                page = requests.get(self.url_json.format(data=data.strftime("%d/%m/%Y")))
                resultados = None

                try:
                    resultados = json.loads(page.text)
                except Exception as e:
                    print(e)
                    quit()

                caderno_qtd_paginas_list_dict = resultados['facetas']['caderno_facet']['valores']

                if not caderno_qtd_paginas_list_dict:
                    self.escreve_log(f'Caderno não disponível no dia {data.strftime("%d/%m/%Y")}')
                    data += timedelta(1)
                    continue

                edicao = resultados['facetas']['edicao_facet']['valores'][0]['valor']

                self.baixa_caderno(caderno_qtd_paginas_list_dict, dict_nome_numero_diario, data, s, edicao)

                proxies = self.create_proxy()
                s.proxies = proxies

            else:

                ConfigManager().escreve_log("Diario não disponível na data {data}".format(data=data.strftime("%d/%m/%Y")), self.robo, self.log)

            data += timedelta(1)


    def baixa_caderno(self, caderno_qtd_paginas_list_dict, dict_nome_numero_diario, data, s, edicao):

        conseguiu = False
        self.tentativas = 0

        for caderno_paginas_dict in caderno_qtd_paginas_list_dict:
            try:

                while not conseguiu and self.tentativas < 5:
                    caderno = []
                    numCaderno = dict_nome_numero_diario[caderno_paginas_dict['valor']]
                    qtd_pags = int(caderno_paginas_dict['quantidade'])
                    name = "DJSC_Caderno{numCaderno}_{data}.pdf".format(numCaderno=numCaderno, data=data.strftime("%Y_%m_%d"))
                    data_arquivo = self.get_data_criacao_arquivo(FileManager(self.robo).caminho(name=name, data=data, por_tipo=False) + f'/txt/{data.year}/{"0" + str(data.month) if len(str(data.month)) == 1 else data.month}/{name}')

                    try:
                        if data_arquivo+timedelta(days=5) > datetime.now():
                            self.escreve_log(f'Caderno {name} baixado a menos de 5 dias')
                            continue
                    except:
                        pass

                    self.escreve_log(f'Coletando o caderno {name}')
                    self.filemanager.download(name, data, self.urldiarios.format(EDICAO=edicao, CADERNO=numCaderno), session=s)
                    #self.baixa_paginas(qtd_pags, s, caderno, numCaderno, data, name)

                    conseguiu = True
                    # ProgressBar(len(list(range(qtd_pags)))).print_progress_bar(len(list(range(qtd_pags))))
                    self.tentativas = 0

            except (DiarioNaoDisponivel, FileNotFoundError) as e:
                ConfigManager().escreve_log(
                    "Diario não disponível na data {data}".format(data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                data += timedelta(1)
                conseguiu = True
                self.tentativas = 0

            except Exception as e:
                ConfigManager().escreve_log(f"Erro para o diário {name}", self.robo, self.log)
                self.tentativas += 1


    def baixa_paginas(self, qtd_pags, s, caderno, numCaderno, data, name):

        for pag in range(1, qtd_pags, 1):
            try:
                page_json = s.get(self.url_download_text_json.format(pagina=pag, data=data.strftime("%Y_%m_%d"), caderno=numCaderno))

                texto_pag = remove_acentos(remove_varios_espacos(json.loads(page_json.text)['resultados'][0]['documento']['integra'].upper()))

                caderno.append(texto_pag + ' ')

                caderno = self.escreve_arquivo_txt(caderno, name, data, pag)

                ProgressBar(len(list(range(qtd_pags)))).print_progress_bar(pag)
                time.sleep(2)

            except Exception as e:

                proxies = self.create_proxy()
                time.sleep(2)

                page_json = s.get(self.url_download_text_json.format(pagina=pag, data=data.strftime("%Y_%m_%d"), caderno=numCaderno), timeout=30, proxies=proxies)
                texto_pag = remove_acentos(remove_varios_espacos(json.loads(page_json.text)['resultados'][0]['documento']['integra'].upper()))
                caderno.append(texto_pag)
                ProgressBar(len(list(range(qtd_pags)))).print_progress_bar(pag)
                time.sleep(2)


    def escreve_arquivo_txt(self, caderno, name, data, pag):

        if len(caderno) % 10 == 0:
            path = FileManager(self.robo).caminho(name=name, data=data, por_tipo=False) + f'/txt/{data.year}/{"0" + str(data.month) if len(str(data.month)) == 1 else data.month}/'

            if not os.path.exists(path):
                os.makedirs(path)

            if not os.path.exists(path):
                file = open(path + name, 'w')
            elif os.path.exists(path) and pag == 1:
                file = open(path + name, 'w')
            else:
                file = open(path + name, 'a+')

            file.writelines(caderno)
            file.close()
            caderno = []

        return caderno


    def get_data_criacao_arquivo(self, path):

        if os.path.exists(path):
            return datetime.fromtimestamp(pathlib.Path(path).stat().st_mtime)
        else:
            return None


    def download_processos(self):
        try:
            ConfigManager().escreve_log("Acessando {}".format(self.__urlprocessos), self.robo, self.log)
            processo = "0000430-67.1996.8.24.0027"

            captcha_decoder = CaptchaSolverESAJ()

            captchas_totais = 0
            captchas_resolvidos = 0

            s = requests.Session()
            s.get(self.__urlprocessos, verify=False, timeout=self.timeout)

            nome = "TJSC_{npu}.html".format(npu=processo)

            conseguiu = False

            while not conseguiu:
                try:
                    tstamp = str(int(time.time()))

                    self.filemanager.download("captcha"+tstamp+".png", None, self.__urlcaptcha.format(time=tstamp),
                                  True, False, 3, s)

                    captcha = captcha_decoder.parse_captcha(os.path.join(self.filemanager.caminho("captcha"+tstamp+".png", None, False),
                                                                         "captcha"+tstamp+".png"))

                    if len(captcha) != 5:
                        ConfigManager().escreve_log("Solução do captcha inválida (resultado: {}). "
                                                    "Tentando novamente...".format(captcha), self.robo, self.log)
                        captchas_totais += 1
                    else:
                        data = s.get(self.__urlprocessosresp.format(local=str(int(processo.split('.')[4])),
                                                                    num_dig_ano=processo.rsplit('.', 4)[0],
                                                                    foro=processo.split('.')[4],
                                                                    npu=processo.replace('-','').replace('.',''),
                                                                    captcha=captcha), timeout=self.timeout)

                        if data.status_code != 200:
                            ConfigManager().escreve_log("Erro ao acessar o servidor: "+ str(data.status_code), self.robo, self.erro)
                            conseguiu = True
                        else:
                            htm = data.content

                            if htm.find("class=\"alert\"") >= 0:
                                ConfigManager().escreve_log("Erro ao resolver captcha (resultado: {}). "
                                                            "Tentando novamente...".format(captcha), self.robo, self.erro)
                            else:
                                conseguiu = True
                                captchas_resolvidos += 1
                                captchas_totais += 1

                            captchas_totais += 1
                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Captcha não pode ser baixado", self.robo, self.erro)
                    conseguiu = True
                except requests.HTTPError as er:
                    ConfigManager().escreve_log("URLError em "+self.__urlprocessos+":" + str(er.message), self.robo, self.erro)
                except Exception as er:
                    ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.erro)

            if captchas_totais > 0:
                ConfigManager().escreve_log("Processos baixados. Precisão na solução dos captchas de {}%.".format(
                    (float(captchas_resolvidos)/float(captchas_totais))*100), self.robo, self.log)
            else:
                ConfigManager().escreve_log("Processos baixados. Nenhum captcha precisou ser resolvido.", self.robo, self.log)

        except requests.HTTPError as er:
            ConfigManager().escreve_log("URLError em "+self.__urlprocessos+":" + str(er.message), self.robo, self.erro)
        except Exception as er:
            ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.erro)


    def data_limite(self):
        return date(2017,10,1)

    def escreve_log(self, txt):
        ConfigManager().escreve_log (f'[{datetime.now ().strftime ("%Y-%m-%d %H:%M")}] ## ' + txt, self.robo, self.log)

if __name__ == '__main__':
    robo = RoboDiarioSC()
    robo.download_atualizacao_diaria()
    print('FOI!!!')




