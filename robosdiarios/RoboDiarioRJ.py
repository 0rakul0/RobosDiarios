# -*- coding: utf-8 -*-


from datetime import datetime, timedelta, date
import os
import traceback
import requests
from bs4 import BeautifulSoup as bs
import json
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.CaptchaSolverRJ import CaptchaSolverRJ
from util.ConfigManager import ConfigManager
import urllib
from util.FileManager import DiarioNaoDisponivel, MaxTentativasExcedidas
import time


class RoboDiarioRJ(RoboDiarioBase):

    def __init__(self):
        self.__url = 'https://www3.tjrj.jus.br/consultadje/pdf.aspx?dtPub={data}&caderno={cad}&pagina=-1'
        super(RoboDiarioRJ, self).__init__("DJRJ", "log_robo_rj.txt", "erro_robo_rj.txt")
        self.timeout = 10

    def get_header(self, s, form=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        if form:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        return headers

    def get_form(self, captcha, soup):
        form = {"__EVENTTARGET": "", "__EVENTARGUMENT": "",
                "__VIEWSTATE":
                    soup.findAll("input", {"id": "__VIEWSTATE"})[0].attrs['value'],
                "__VIEWSTATEGENERATOR":
                    soup.findAll("input", {"id": "__VIEWSTATEGENERATOR"})[0].attrs['value'],
                "__EVENTVALIDATION":
                    soup.findAll("input", {"id": "__EVENTVALIDATION"})[0].attrs['value'],
                "CaptchaControl1": captcha,
                "Button1": "Validar"}
        return form

    def get_captcha(self, s, captcha_decoder, url_captcha):
        captcha = ""
        captcha_name = "captcha.jpg"

        try:
            self.filemanager.download(captcha_name, None, "https://www3.tjrj.jus.br/consultadje/" + url_captcha,
                      True, False, 3, s)
            captcha = captcha_decoder.parse_captcha(os.path.join(self.filemanager.caminho(captcha_name, None, False),
                                                             captcha_name))
        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                ConfigManager().escreve_log("Captcha não pode ser baixado: " + traceback.format_exc(), self.robo, self.erro)

        return captcha

    def get_diario(self, s, cod, data, cadernos, captcha_decoder, captchas_totais):
        ConfigManager().escreve_log("DJRJ_{caderno}_{data}.pdf - "
                                    "Baixando...".
                                    format(caderno=cadernos[cod],
                                           data=data.strftime("%Y_%m_%d")), self.robo, self.log)
        self.tentativas = 0
        self.tentativas_captcha = 0

        nome = "DJRJ_{caderno}_{data}.pdf".format(caderno=cadernos[cod],
                                                        data=data.strftime("%Y_%m_%d"))

        possivel_pdf = os.path.join(self.filemanager.caminho(nome, data, True), nome)

        if os.path.isfile(possivel_pdf):
            ConfigManager().escreve_log("Diário {} já acessado. Pulando...".format(nome), self.robo, self.log)
        else:
            conseguiu_pg = False

            while not conseguiu_pg:
                resp = s.get(self.__url.format(data=data.strftime("%d/%m/%Y"), cad=cod), verify=False,
                             timeout=self.timeout)
                html = resp.content
                soup = bs(html, "html5lib")

                url_captcha = None

                for img in soup.findAll('img'):
                    if img['src'].startswith("CaptchaImage"):
                        url_captcha = img['src']

                try:
                    if url_captcha is None:
                        conseguiu_pg = self.__download_pdf(resp, nome, data)

                        if not conseguiu_pg:
                            raise DiarioNaoDisponivel("Diário não disponível em {data}...".format(data=data.strftime("%d/%m/%Y")))
                    else:
                        captcha = self.get_captcha(s, captcha_decoder, url_captcha)

                        if len(captcha) != 5:
                            ConfigManager().escreve_log("Solução do captcha inválida (resultado: {}). "
                                                        "Tentando novamente...".format(captcha), self.robo, self.log)
                            self.tentativas_captcha += 1
                            captchas_totais += 1
                        else:
                            # Aguardando o tempo mínimo do captcha
                            time.sleep(5)

                            form = self.get_form(captcha, soup)

                            headers = self.get_header(s, form)

                            resp = s.post(self.__url.format(data=data.strftime("%d/%m/%Y"), cad=cod),
                                          verify=False, timeout=self.timeout, headers=headers,
                                          data=urllib.parse.urlencode(form))
                            resp = s.get(self.__url.format(data=data.strftime("%d/%m/%Y"), cad=cod), verify=False,
                                 timeout=self.timeout)

                            if resp.status_code == 200 and "HTML" in str(resp.content):
                                ConfigManager().escreve_log("Possível solução: {captcha}".format(captcha=captcha), self.robo, self.log)
                                conseguiu_pg = False
                            elif resp.status_code != 302 and resp.status_code != 200:
                                ConfigManager().escreve_log("Erro ao acessar diário: " + str(resp.status_code), self.robo, self.erro)
                                self.tentativas += 1
                                conseguiu_pg = False
                            else:
                                ConfigManager().escreve_log("Possível solução: {captcha}".format(captcha=captcha), self.robo, self.log)
                                conseguiu_pg = self.__download_pdf(resp, nome, data)

                                if not conseguiu_pg:
                                    ConfigManager().escreve_log("Erro ao resolver captcha: " + captcha, self.robo, self.erro)
                                    self.tentativas += 1
                except DiarioNaoDisponivel as dne:
                    raise dne
                except MaxTentativasExcedidas as mte:
                    raise mte
                except Exception as e:
                    ConfigManager().escreve_log("Erro ao acessar diário: " + traceback.format_exc(), self.robo, self.erro)
                    self.tentativas += 1
                    conseguiu_pg = False


    def download_atualizacao_diaria(self):
        cadernos = {"A": "Administrativo", "S": "Judicial_-_2_Instancia", "C": "Judicial_-_1_Instancia_Capital",
                    "I": "Judicial_-_1_Instancia_Interior", "E": "Edital"}


        ConfigManager().escreve_log("Acessando {}".format(self.__url), self.robo, self.log)

        captcha_decoder = CaptchaSolverRJ()

        captchas_totais = 0
        captchas_resolvidos = 0

        atual = datetime.now().date()

        s = requests.Session()

        for cod in cadernos:
            data = self.data_inicial("DJRJ_{caderno}".format(caderno=cadernos[cod]))

            while atual >= data:
                conseguiu = False
                self.tentativas = 0
                self.tentativas_captcha = 0

                name = "DJRJ_{caderno}_{data}.pdf".format(caderno=cadernos[cod],data=data.strftime("%Y_%m_%d"))

                final = os.path.join(self.filemanager.caminho(name, data, True), name)

                if os.path.isfile(final):
                    ConfigManager().escreve_log("{} já acessado. Pulando...".format(name), self.robo, self.log)
                else:
                    while not conseguiu:
                        try:
                            self.get_diario(s, cod, data, cadernos, captcha_decoder, captchas_totais)
                            conseguiu = True
                        except DiarioNaoDisponivel:
                            ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.log)
                            conseguiu = True
                        except:
                            ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.robo, self.erro)
                            if os.path.isfile(final):
                                os.remove(final)
                            raise

                data += timedelta(1)

    def __download_pdf(self, resp, nome, data):
        if resp.headers['content-type'] == 'application/pdf':
            self.filemanager.download_stream(nome, data, resp.content, False, True)
            return True
        else:
            return False

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioRJ()
    robo.download_atualizacao_diaria()