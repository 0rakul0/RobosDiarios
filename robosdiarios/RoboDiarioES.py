from datetime import timedelta, datetime, date
import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from util.ConfigManager import ConfigManager
from dateutil.relativedelta import relativedelta
from util import DateUtil as d
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha


class RoboDiarioES(RoboDiarioBase):
    def __init__(self):
        self.url_acervo_atual = 'https://sistemas.tjes.jus.br/ediario/index.php?option=com_ediario&view=contents&layout=fulltext&data={data}' # ex: 20200812
        self.url_acervo_anterior_2003 = 'http://diario.tjes.jus.br/{ano}/{data}.pdf' # 20000801 até 20130823
        super(RoboDiarioES, self).__init__("DJES", "log_robo_es.txt", "erro_robo_es.txt")

    def atualiza_acervo_2023_to_atual(self, data=None):
        atual = datetime.now().date()
        op = Options()
        op.add_argument('--headless') # para abrir o navegador comentar essa linha
        driver = webdriver.Chrome(executable_path=r'../chrome/chromedriver', options=op)

        if not data:
            data = date(2013, 8, 24)

        while atual >= data:
            data_str = str(data)
            try:
                nome_caderno = 'DJES_{}.txt'.format(data_str.replace('-', '_'))
                self.escreve_log('Acessando diário do dia {}'.format(data_str))

                if self.filemanager.ja_baixado(nome_caderno, data, por_tipo=True, subfolders=None):
                    self.escreve_log("{} já existe. Pulando...".format(nome_caderno))

                else:

                    driver.get(self.url_acervo_atual.format(data=data_str.replace('-', '')))
                    soup = bs(driver.page_source, 'html.parser')
                    ano_na_pag = soup.find('a', {'id': 'ano-calendario'})

                    if atual.year == int(ano_na_pag.text.split()[0]) and atual != data:
                        if d.parse_mes_por_extenso(atual.month) == \
                                soup.find('a', {'id': 'mes-calendario'}).text.split()[0]:
                            self.escreve_log('Diário indisponível no dia {}'.format(data_str))
                            data += relativedelta(days=+1)
                            continue

                    caderno = soup.find('div', {'class': 'materia container12 grid_9'})
                    caderno_text = [remove_varios_espacos(cad.text) for cad in caderno.find_all()[2:]]

                    path = self.filemanager.caminho(nome_caderno, data)

                    self.escreve_log('Baixando o diário {}'.format(nome_caderno))
                    with open(file=os.path.join(path, nome_caderno), mode='w', encoding='utf-8') as f:
                        for line in caderno_text:
                            if line is '':
                                f.write('\n')
                            else:
                                f.write(line)
                        f.flush()
                        os.fsync(f.fileno())
                    self.escreve_log('Baixou o diário {}'.format(nome_caderno))
            except Exception as e:
                print(e)

            data += relativedelta(days=+1)


    def atualiza_acervo_2013_to_atual(self, data=None):
        s = requests.Session()
        atual = datetime.now().date()
        if not data:
            data = date(2013,8,24)

        while atual >= data:
            data_str=str(data)
            try:
                nome_caderno = 'DJES_{}.txt'.format (data_str.replace ('-', '_'))
                self.escreve_log ('Acessando diário do dia {}'.format (data_str))

                if self.filemanager.ja_baixado (nome_caderno, data, por_tipo=True, subfolders=None):
                    self.escreve_log ("{} já existe. Pulando...".format (nome_caderno))

                else:
                    html = s.get(self.url_acervo_atual.format(data=data_str.replace('-', '')))
                    soup = bs (html.text.replace ('<!-- ', '').replace (' -->', ''), 'html5lib')
                    ano_na_pag = soup.find ('a', {'id': 'ano-calendario'})

                    if atual.year == int(ano_na_pag.text.split()[0]) and atual != data:
                        if d.parse_mes_por_extenso (atual.month) == soup.find ('a', {'id': 'mes-calendario'}).text.split ()[0]:
                            self.escreve_log ('Diário indisponível no dia {}'.format (data_str))
                            data += relativedelta (days=+1)
                            continue

                    caderno = soup.find ('div', {'class': 'materia container12 grid_9'})
                    caderno_text = [remove_varios_espacos (cad.text) for cad in caderno.find_all ()[2:]]

                    path = self.filemanager.caminho (nome_caderno, data)

                    self.escreve_log('Baixando o diário {}'.format(nome_caderno))
                    with open (file=os.path.join (path, nome_caderno), mode='w', encoding='utf-8') as f:
                        for line in caderno_text:
                            if line is '':
                                f.write('\n')
                            else:
                                f.write(line)
                        f.flush ()
                        os.fsync(f.fileno())

                    self.escreve_log('Baixou o diário {}'.format(nome_caderno))

            except Exception as e:
                print(e)

            data += relativedelta(days=+1)


    def atualiza_acervo_anterior_2013(self):
        s = requests.Session()
        atual = date(2013,8,23)
        data = date(2000,8,5)

        while atual >= data:
            name = 'DJES_{}.pdf'.format(str(data).replace('-','_'))
            self.escreve_log ('Acessando diário do dia {}'.format (str(data)))
            html = s.get(self.url_acervo_anterior_2003.format(ano=data.year,data=str(data).replace('-','')))
            if html.status_code == 200:
                self.escreve_log ('Baixando o diário {}'.format (name))
                baixou = self.filemanager.download(name,data,self.url_acervo_anterior_2003.format(ano=data.year,data=str(data).replace('-','')), session=s)
                if baixou:
                    self.escreve_log ('Baixou o diário {}'.format (name))
                else:
                    self.escreve_log('Erro ao baixar o diário {}'.format(name))
            else:
                self.escreve_log('Diário não disponível no dia {}'.format(str(data)))

            data += relativedelta(days=+1)


    def download_atualizacao_diaria(self):
        data = self.data_inicial('DJES')
        self.atualiza_acervo_2023_to_atual(data)


    def escreve_log(self, txt):
        ConfigManager ().escreve_log ('[' + datetime.now ().strftime ("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo, self.log)


    def data_limite(self):
        return date(2023,7,20)


if __name__ == '__main__':
    robo = RoboDiarioES()
    robo.escreve_log('########### INÍCIO ROBÔ DJES ###########')
    robo.atualiza_acervo_2023_to_atual()
    # robo.download_atualizacao_diaria()
    # robo.atualiza_acervo_2013_to_atual()
    # robo.atualiza_acervo_anterior_2013()
    robo.escreve_log('########### FIM ROBÔ DJES ###########')



