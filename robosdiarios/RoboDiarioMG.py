# -*- coding: utf-8 -*-



from datetime import date, datetime, timedelta
import requests
import os
import time
import traceback
import zipfile
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.CaptchaSolverMG import CaptchaSolverMG
import random

import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioMG(RoboDiarioBase):

    def __init__(self):
        self.__url = "http://www8.tjmg.jus.br/juridico/diario/index.jsp"
        self.url_datas = 'https://dje.tjmg.jus.br/diarioJudiciarioMesAno.do?mes={mes}&ano={ano}&tipoDiario={comarca}&lista=Pesquisar+Diarios'
        self.__urlantigos = "https://dje.tjmg.jus.br/diarioJudiciarioData.do"
        self.__urlpost = "https://dje.tjmg.jus.br/pesquisarDiarioJudiciario.do"
        super(RoboDiarioMG, self).__init__("DJMG", "log_robo_mg.txt", "erro_robo_mg.txt")

    def download_antigos(self, data_inicio=None, data_fim=None):
        try:
            ConfigManager().escreve_log("Acessando {}".format(self.__urlantigos), self.robo, self.log)

            res = requests.get(self.__urlantigos, verify=False)
            html = res.content

            soup = bs(html, "html5lib")
            comarcacmb = soup.findAll("select", {"id": "tipoDiario"})[0]

            if data_inicio and data_fim:
                final = data_fim
                atual = data_inicio
            elif data_inicio:
                final = datetime.now().date()
                atual = data_inicio
            else:
                final = date(2010,12,31)#datetime.now().date()
                atual = date(2009,1,5)#self.data_inicial('DJMG')

            # final = 2010, 12, 17 / 2013, 12, 19 / 2016, 12, 19 / 2018, 12, 19
            # atual = 2008, 8, 22 / 2011, 1, 10 / 2014, 1, 7 / 2017, 1, 9

            comarcas = []

            for child in comarcacmb.descendants:
                if type(child) is Tag:
                    for option in child.findAll("option"):
                        comarcas.append(option.attrs["value"])

            captcha_decoder = CaptchaSolverMG()

            captchas_totais = 0
            captchas_resolvidos = 0

            #requests.packages.urllib3.disable_warnings()

            s = requests.Session()
            s.get(self.__urlantigos, verify=False, timeout=self.filemanager.timeout)

            while atual < final:

                if atual.isoweekday() == 6:
                    atual += timedelta(2)
                    print('Não houve diário pois a data é referente ao dia da semana "Sábado". Pulando para a data {}'.format(atual))
                    continue
                if atual.isoweekday() == 7:
                    atual += timedelta(1)
                    print('Não houve diário pois a data é referente ao dia da semana "Domingo". Pulando para a data {}'.format(atual))
                    continue

                for comarca in comarcas:
                    conseguiu = False
                    self.tentativas = 0

                    nome = "DJMG_{nome}_{data}".format(nome=comarca.replace('|', '-'),
                                                       data=atual.strftime("%Y_%m_%d")) + ".pdf"

                    try:
                        datas = s.get(self.url_datas.format(mes=atual.month, ano=atual.year, comarca=comarca), verify=False)
                    except OSError:
                        s = requests.Session()
                        time.sleep(2)
                        datas = s.get(self.url_datas.format(mes=atual.month, ano=atual.year, comarca=comarca), verify=False)

                    soup_datas = bs(datas.text, 'html5lib').find_all('td', {'class': 'corpo'})
                    datas_disponiveis = [d.find('div', {'align': 'left'}).text.split('de')[0].strip() for d in soup_datas]

                    if str(atual.day) not in datas_disponiveis:
                        print('Caderno {} não disponível nesta data'.format(nome))
                        continue

                    possivel_pdf = os.path.join(self.filemanager.caminho("*.pdf", atual, True), nome)

                    if os.path.isfile(possivel_pdf):
                        ConfigManager().escreve_log("{} já acessado. Pulando...".format(nome), self.robo, self.log)
                    else:
                        while not conseguiu:
                            try:
                                rnd = str(random.uniform(0, 5))
                                captcha_src = "captcha.svl?" + rnd
                                data = datetime.now()
                                self.filemanager.download("captcha"+rnd+".svl",data,"https://dje.tjmg.jus.br/" + captcha_src,
                                                          True, False, 3,s, print_baixou=False)

                                captcha = captcha_decoder.parse_captcha(os.path.join(self.filemanager.caminho(name="captcha"+rnd+".svl", por_tipo=False), "captcha"+rnd+".svl"))

                                if len(captcha) != 5:
                                    ConfigManager().escreve_log("Solução do captcha inválida (resultado: {}). "
                                                                "Tentando novamente...".format(captcha), self.robo, self.log)
                                    captchas_totais += 1
                                else:
                                    params = {
                                        "data": atual.strftime("%d/%m/%Y"), "tipoDiario": comarca.strip(),
                                        "captcha_text": captcha
                                    }
                                    # "Content-Length": len(urllib.parse.urlencode({"data": atual.strftime("%d/%m/%Y"),
                                    #                                               "tipoDiario": comarca.strip(),
                                    #                                               "captcha_text": captcha}))
                                    #"DNT": 1,
                                    headers = {
                                        "Host": "dje.tjmg.jus.br",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
                                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                                        "Accept-Encoding": "gzip, deflate, br",
                                        "Referer": "https://dje.tjmg.jus.br/diarioJudiciarioData.do",
                                        "Cookie": "__utma=175023463.1070609321.1436451212.1437050520.1437067435.5; "
                                                  "__utmz=175023463.1436451212.1.1.utmcsr=google|utmccn=(organic)|"
                                                  "utmcmd=organic|utmctr=(not%20provided); "
                                                  "JSESSIONID="+ s.cookies["JSESSIONID"],
                                        "Connection": "keep-alive",
                                        "Content-Length": "64",
                                        "Content-Type": "application/x-www-form-urlencoded"
                                    }

                                    data = s.post(self.__urlpost, data=params, headers=headers, timeout=self.timeout)

                                    if data.status_code != 200:
                                        ConfigManager().escreve_log("Erro ao acessar o servidor: " +
                                                                    str(data.status_code), self.robo, self.erro)
                                        conseguiu = True
                                    elif data.headers['content-type'] == 'application/pdf':
                                        conseguiu = True
                                        ConfigManager().escreve_log("Baixando PDF {}...".format(nome), self.robo, self.log)
                                        self.filemanager.download_stream(nome, atual, data.content, False, True)

                                        captchas_resolvidos += 1
                                        captchas_totais += 1
                                    else:
                                        htm = data.content

                                        if str(htm).find("class=\"aviso\"") >= 0:
                                            ConfigManager().escreve_log("Diário não disponível para {} em "
                                                                        "{}. Pulando...".format(comarca,
                                                                                                atual.strftime("%d/%m/%Y")), self.robo, self.log)
                                            conseguiu = True
                                        else:
                                            ConfigManager().escreve_log("Erro ao resolver captcha (resultado: {}). "
                                                                        "Tentando novamente...".format(captcha), self.robo, self.log)
                                        captchas_totais += 1
                            except (DiarioNaoDisponivel, FileNotFoundError) as e:
                                ConfigManager().escreve_log("Captcha não pode ser baixado", self.robo, self.erro)
                                conseguiu = True
                            except Exception as er:
                                ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.erro)
                                self.tentativas += 1
                atual += timedelta(1)

            if captchas_totais > 0:
                ConfigManager().escreve_log("PDFs baixados. Precisão na solução dos captchas de {}%.".format(
                    (float(captchas_resolvidos)/float(captchas_totais))*100), self.robo, self.log)
            else:
                ConfigManager().escreve_log("PDFs baixados. Nenhum captcha precisou ser resolvido.", self.robo, self.log)

        except requests.HTTPError as er:
            ConfigManager().escreve_log("URLError em "+self.__urlantigos+":" + str(er.message), self.robo, self.erro)
        except Exception as er:
            ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.erro)


    def download_atualizacao_diaria(self):
        #requests.packages.urllib3.disable_warnings()
        ConfigManager().escreve_log("Acessando {}".format(self.__url), self.robo, self.log)
        html = requests.get(self.__url, verify=False, timeout=self.timeout).text #urlopen(self.__url).read()
        soup = bs(html.replace("ISO-8859-1", "utf-8"), "html5lib")
        comarcacmb = soup.findAll("select", {"id": "selCompleta"})[0]

        atual = datetime.now().date()

        comarcas = []

        for child in comarcacmb.descendants:
            if type(child) is Tag:
                for option in child.findAll("option"):
                    comarcas.append(option.attrs["value"])

        for comarca in comarcas:
            data = self.data_inicial("DJMG_{nome}".format(nome=comarca.replace('|', '-')))

            while atual >= data:
                urldiario = self.__url + "?dia={dia:02d}{mes:02d}&completa={comarca}".format(dia=data.day, mes=data.month, comarca=comarca.strip())
                nome = "DJMG_{nome}_{data}".format(nome=comarca.replace('|', '-'),
                                                        data=data.strftime("%Y_%m_%d"))

                possivel_html = os.path.join(self.filemanager.caminho("*.html", data, True), nome + ".html")
                possivel_zip = os.path.join(self.filemanager.caminho("*.zip", data, False), nome + ".zip")
                possivel_rtf = os.path.join(self.filemanager.caminho("*.rtf", data, True), nome + ".rtf")

                if os.path.isfile(possivel_html) or os.path.isfile(possivel_zip) or os.path.isfile(possivel_rtf):
                    if data == atual:
                        ConfigManager().escreve_log("{} já acessado. Pulando...".format(nome), self.robo, self.log)
                else:
                    conseguiu = False

                    while not conseguiu:
                        try:
                            htmldiario = requests.get(urldiario, verify=False, timeout=self.timeout).text #urlopen(urldiario).read()
                            soup = bs(htmldiario.replace("ISO-8859-1", "utf-8"), "html5lib")

                            zip = None

                            divzip = soup.findAll("div", {"class": "corpo"})

                            if divzip:
                                i = 0

                                while i < len(divzip) and zip is None:
                                    links = divzip[i].findAll("a")

                                    if links:
                                        if links[i].has_attr("href"):
                                            if links[i].attrs["href"].endswith(".zip"):
                                                zip = self.__url.rsplit("/", 1)[0] + "/" + \
                                                    links[i].attrs["href"]
                                    i += 1

                            if zip is None:
                                nome += ".html"
                                ConfigManager().escreve_log("Buscando {} em {}...".format(nome, urldiario), self.robo, self.log)
                                self.filemanager.download(nome, data, urldiario, False, True, 5)
                                self.inserir_no_banco_para_extrair(nome)
                            else:
                                nome += ".zip"
                                ConfigManager().escreve_log("Buscando {} em {}...".format(nome, urldiario), self.robo, self.log)
                                self.filemanager.download(nome, data, zip, False, False, 5)

                                zfile = open(os.path.join(self.filemanager.caminho(nome, data, False), nome), 'rb')
                                z = zipfile.ZipFile(zfile)
                                z.extract(z.namelist()[0], self.filemanager.caminho(nome, data, False))
                                zfile.close()

                                rtf = os.path.splitext(nome)[0] + ".rtf"
                                os.rename(
                                    os.path.join(self.filemanager.caminho(nome, data, False), z.namelist()[0]),
                                    os.path.join(self.filemanager.caminho(rtf, data, True), rtf)
                                )

                                os.remove(os.path.join(self.filemanager.caminho(nome, data, False), nome))
                            conseguiu = True
                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                            ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                                data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                            conseguiu = True
                        except Exception as er:
                            ConfigManager().escreve_log("Erro: " + traceback.format_exc(er), self.robo, self.erro)
                            self.tentativas += 1
        data += timedelta(1)

    def data_limite(self):
        #return date(2018, 3, 23)
        return date(2008, 5, 29)


if __name__ == '__main__':
    robo = RoboDiarioMG()
    if len(sys.argv) == 3:
        data_inicio = datetime.strptime(sys.argv[1],'%Y/%m/%d').date()
        data_fim = datetime.strptime(sys.argv[2],'%Y/%m/%d').date()
        robo.download_antigos(data_inicio=data_inicio, data_fim=data_fim)
    elif len(sys.argv) == 2:
        data_inicio = datetime.strptime(sys.argv[1], '%Y/%m/%d').date()
        robo.download_antigos(data_inicio=data_inicio)
    else:
        robo.download_antigos()