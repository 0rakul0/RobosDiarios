from datetime import datetime, date
import calendar
import os
import traceback
import requests
import re
import time
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from util.DateUtil import daterange
from util.MultiprocessWorkManager import WorkManager, DownloadTask, MergeTask


class RoboDiarioTRF1(RoboDiarioBase):
    """
    Robo responsavel pelo download de diarios oficias do TRF1.
    """

    def __init__(self):
        self.__url_trf1 = "" \
                          "https://edj.trf1.jus.br/edj/discover?rpp=10&etal=0&scope=123/471&group_by=none&page={pagina}&sort_by=2&order=DESC&filtertype_0=dateIssued&filtertype_1=title&filter_relational_operator_1=contains&filter_relational_operator_0=equals&filter_1=&filter_0={data}"
        super(RoboDiarioTRF1, self).__init__("TRF01", "TRF1_robodiario.txt", "TRF1_robodiario.err")

    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return date(2007, 10, 26)

    def download_atualizacao_diaria(self, verifica_todo_periodo=False):
        """
        Define o intervalo de tempo dos diarios que devem ser baixados.

        Args:
            verifica_todo_periodo(bool): define se o download deve começar de uma data especifica ou do da data atual.

        """
        if verifica_todo_periodo:
            # start_date = date(2007, 10, 26)
            start_date = date(2019, 5, 15)
        else:
            start_date = self.data_inicial("TRF01")

        for data in daterange(start_date, datetime.now().date()):

            if data < date(2009, 10, 6):
                # self.__download_trf1_antigo(data)
                pass
            elif data < date(2015, 1, 1):
                self.__download_trf1_2009a2015(data)
            else:
                self.download_trf1(data)

    def download_trf1(self, data):
        """
        Faz o download dos diarios oficiais de acordo com data, para diarios a partir de 2015.
        """
        base_url = 'https://edj.trf1.jus.br'
        url = 'https://edj.trf1.jus.br/edj/handle/123/3/discover?filtertype_1=dateIssued&filter_relational_operator_1=equals&filter_1={DATA}&submit_apply_filter=Aplicar&rpp=20&sort_by=dc.date.accessioned_dt'
        search_url = url.format(DATA=data.strftime('%Y-%m-%d'))

        requested_page = requests.get(search_url)

        soup = bs(requested_page.text, 'html5lib')

        self.escreve_log('Acessando cadernos do dia {}'.format(data.strftime('%Y-%m-%d')))

        pdf_urls = [base_url + x.attrs['href'] for x in soup.select(
            '#aspect_discovery_SimpleSearch_div_search-results > ul > ul > li > div.artifact-description > div.artifact-title > a')]

        if len(pdf_urls) is 0:
            self.escreve_log('Não existem diário do dia {}'.format(data.strftime('%Y-%m-%d')))

        for pdf_url in pdf_urls:
            requested_page = requests.get(pdf_url)
            soup = bs(requested_page.text, 'html5lib')
            counter = 1
            # for link in [base_url + x.attrs['href'] for x in soup.select('#aspect_artifactbrowser_ItemViewer_div_item-view > div > div > div.file-metadata > div > ul > li > a')]:
            # link = base_url + soup.select('#aspect_artifactbrowser_ItemViewer_div_item-view > div > div > div.file-metadata > div > ul > li > a')[0].attrs['href']
            for files in soup.select(
                    '#aspect_artifactbrowser_ItemViewer_div_item-view > div > div > div.file-metadata'):
                link = base_url + files.select_one('div > ul > li > a').attrs['href']
                filename = files.select_one('div > ul > li').text.replace(' ', '')
                if not "_" in filename and "ADM" in filename:
                    continue
                caderno = filename.split('_')[1]
                secao = filename.split('_')[2]
                if 'Parte1' in filename:
                    caderno += '1'
                elif 'Parte2' in filename:
                    caderno += '2'
                elif 'Parte3' in filename:
                    caderno += '3'
                elif 'Parte4' in filename:
                    caderno += '4'
                elif 'Parte5' in filename:
                    caderno += '5'
                elif 'Parte6' in filename:
                    caderno += '6'
                elif 'Parte' in filename:
                    caderno += str(counter)
                counter += 1
                name = 'TRF01_{CADERNO}_{SECAO}_{DATA}.pdf'.format(DATA=data.strftime('%Y_%m_%d'), CADERNO=caderno,
                                                                   SECAO=secao)
                self.escreve_log('Baixando o caderno {}'.format(name))
                self.filemanager.download(name, data, link, stream=True)

    def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True, somente_inicio_mes=False, subfolders=None):
        """
        Retorna a data do ultimo diario baixado.
        """
        data = super(RoboDiarioTRF1, self).data_inicial(filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self, txt):
        """
        Cria arquivo de log referente a execução do robo.
        """
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,
                                    self.log)

    def download_trf1_old(self, curr_date, verifica_todo_periodo=False):

        self.escreve_log('########### INICIO TRF01 ###########')

        self.tentativas = 0

        ano_atual = curr_date.year
        mes_atual = curr_date.month
        dia_atual = curr_date.day
        url = self.__url_trf1
        pagina = 1

        try:

            r = requests.get(url.format(pagina=pagina, data=str(ano_atual) + '-' + str(
                "{:02d}".format(mes_atual)) + '-' + str("{:02d}".format(dia_atual))),
                             verify=False)

            soup = bs(r.text, "html5lib")

            list_pags = soup.find('ul', {'class': 'pagination-links'})

            if list_pags:
                i = 0
                limite = len(list_pags.find_all("li")[:-1])

                for li_paginas in list_pags.find_all("li")[:-1]:

                    link_paginas = li_paginas.find("a")

                    i += 1

                    link_passagem_paginas = "https://edj.trf1.jus.br/edj/" + link_paginas["href"]

                    r = requests.get(link_passagem_paginas)

                    soup = bs(r.text, "html5lib")

                    for div in soup.find_all('div', {'class': 'artifact-title'}):

                        # cada div é relativa a um caderno, um pdf
                        a = div.find('a')

                        link = 'https://edj.trf1.jus.br' + a['href']

                        pg_download = requests.get(link)

                        soup_down = bs(pg_download.text, "html5lib")

                        divs_down = soup_down.find_all('div', {'class': 'file-metadata'})

                        div_data = soup_down.find('div', {'class': 'ds-static-div primary'})

                        data = datetime.strptime(
                            re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', div_data.find('h1').text).group(0),
                            '%Y-%m-%d')

                        pdfs = []
                        saida = None

                        try:
                            caderno = soup_down.find('div', {
                                'id': 'aspect_artifactbrowser_ItemViewer_div_item-view'}).find('h1').next
                            rgx = re.search('Caderno([a-zA-Z]{1,}\s)*\s?-(.{4}) de [0-9\-]{10}', caderno)
                            caderno = rgx.group(2).replace(" ", "").replace("CADERNODEEDITAISJUDICIAIS",
                                                                            "EDTJUD")
                            tipo_caderno = rgx.group(1).strip()

                            if tipo_caderno == "Judicial":
                                tipo_caderno = "JUD"
                            elif tipo_caderno == "Administrativo":
                                tipo_caderno = "ADM"
                            else:
                                tipo_caderno = "EDJ"

                        except:
                            print("Erro", caderno)

                        for div_down in divs_down:
                            link_down = 'https://edj.trf1.jus.br' + div_down.find('a')['href']
                            data_caderno = re.search(
                                '(PARTE([0-9]+)-)?CADERNO_(.*?)_([0-9]{4}-[0-9]{2}-[0-9]{2})',
                                link_down.upper())

                            if data_caderno:
                                parte = data_caderno.group(2)

                                if not saida:
                                    saida = "TRF01_{TIPOCADERNO}_{CADERNO}_{DATA}.pdf".format(
                                        DATA=data.strftime("%Y_%m_%d"),
                                        CADERNO=caderno.upper(),
                                        TIPOCADERNO=tipo_caderno)
                            else:
                                parte = None

                            name = "TRF01_{TIPOCADERNO}_{CADERNO}_{DATA}{PARTE}.pdf".format(
                                DATA=data.strftime("%Y_%m_%d"),
                                CADERNO=caderno.upper(),
                                PARTE=('_' + parte) if parte else '',
                                TIPOCADERNO=tipo_caderno)

                            if self.filemanager.download(name, data, link_down):
                                pdfs.append(
                                    os.path.join(self.filemanager.caminho(name, data),
                                                 name))

                        if len(pdfs) > 1:
                            saida = os.path.join(self.filemanager.caminho(name, data)) + os.path.sep + saida
                            self.filemanager.juntar_pdfs(saida, pdfs, apagar_arquivos=True, ordenar=False)

                        pdfs.clear()

        except(DiarioNaoDisponivel, FileNotFoundError) as e:
            ConfigManager().escreve_log("Diario não disponível no ano {data}".format(
                data=str(ano_atual)), self.robo, self.log)
            mes_atual += 1
        except Exception as e:
            print(e)
            ConfigManager().escreve_log("Erro: " + traceback.format_exc(), self.erro, self.log)
            self.tentativas += 1
            pagina = 1

        self.escreve_log('########### FIM TRF01 ###########')

    def __download_trf1_2009a2015(self, data):
        """
        Faz o download dos diarios oficiais de acordo com data, para diarios de 2009 a 2015.
        """
        # http://portal.trf1.jus.br/dspace/discover?filtertype_0=dateIssued&filter_relational_operator_0=equals&filter_0={DATA}&filtertype_3=title&filter_relational_operator_3=contains&filter_3=&submit_apply_filter=Aplicar&query=&scope=123%2F163457
        base_url = 'http://portal.trf1.jus.br'
        url = 'http://portal.trf1.jus.br/dspace/discover?filtertype_0=dateIssued&filter_relational_operator_0=equals&filter_0={DATA}&filtertype_3=title&filter_relational_operator_3=contains&filter_3=&submit_apply_filter=Aplicar&query=&scope=123%2F163457'

        search_url = url.format(DATA=data)

        requested_page = requests.get(search_url)

        soup = bs(requested_page.text, 'html5lib')

        pdf_urls = [base_url + x.attrs['href'] for x in soup.select(
            '#aspect_discovery_SimpleSearch_div_search-results > ul > ul > li > div.artifact-description > div.artifact-title > a')]

        for pdf_url in pdf_urls:
            requested_page = requests.get(pdf_url)
            soup = bs(requested_page.text, 'html5lib')
            link = base_url + soup.select('div.file-link > a')[0].attrs['href']
            name = 'TRF01_UNICO_{DATA}.pdf'.format(DATA=data.strftime('%Y_%m_%d'))
            self.filemanager.download(name, data, link, stream=True)

    def __download_trf1_imprensanacional(self):

        """ DEPRECATED
        baixa os eDJF1 entre 06/10/2009 e 12/2014
        fonte: http://pesquisa.in.gov.br/imprensa/core/startDjEdjf1.action
        form: http://pesquisa.in.gov.br/imprensa/core/consultaDjEdjf1.action
        :return: None
        """

        # start_date = date(2009, 10, 6)
        start_date = date(2014, 8, 17)
        end_date = date(2015, 12, 31)
        # end_date = date(2009, 10, 20)

        mpw = WorkManager(6)  # i/o bound process

        connection_down = False

        for data in daterange(start_date, end_date):

            if connection_down:
                break

            tentativas = 0  # cada data é tentada no máximo 3x

            while tentativas < 3:
                print("Baixando diario do dia", data.strftime("%d-%m-%Y"), end='')

                datastr = data.strftime('%Y_%m_%d')
                name = "TRF01_COMPLETO_{DATA}.pdf".format(DATA=datastr)

                if self.filemanager.ja_baixado(name, data, modo=False):  # pdf apos merge
                    print()
                    break  # buscar próxima data

                else:

                    params = {'edicao.jornal_hidden': '',
                              'edicao.txtPesquisa': '',
                              'edicao.jornal': '20,21',
                              'edicao.fonetica': 'null',
                              'edicao.dtInicio': '{DIA}/{MES}'.format(DIA=data.day, MES=data.month),
                              'edicao.dtFim': '{DIA}/{MES}'.format(DIA=data.day, MES=data.month),
                              'edicao.ano': '{ANO}'.format(ANO=data.year)
                              }

                    try:
                        pagina = requests.post('http://pesquisa.in.gov.br/imprensa/core/consultaDjEdjf1.action',
                                               data=params,
                                               verify=False, timeout=self.timeout)
                    except requests.exceptions.ProxyError:
                        print("Erro de proxy, tentando novamente")
                        tentativas += 1

                        if tentativas == 3:
                            print("Numero de tentativas esgotadas. Verificar a conexão com a internet.")
                            connection_down = True

                        continue

                    except requests.exceptions.ReadTimeout:
                        print(" Timeout... Tentando novamente")
                        tentativas += 1

                        if tentativas == 3:
                            print("Numero de tentativas esgotadas. Verificar a conexão com a internet.")
                            connection_down = True

                        continue  # volta para o inicio do loop while
                    except requests.exceptions.ConnectionError:
                        print(" Connection error... Tentando novamente")
                        tentativas += 1

                        if tentativas == 3:
                            print("Numero de tentativas esgotadas. Verificar a conexão com a internet.")
                            connection_down = True

                        continue  # volta para o inicio do loop while

                    # html > body > table#ResultadoConsulta > tbody > tr > th > a
                    if re.search('<table.{1,}id="ResultadoConsulta".{1,}>', pagina.text,
                                 re.I):  # consulta retornou resultados
                        soup = bs(pagina.text, "html5lib")

                        for th_resultado in [x.find_all("th")[0] for x in
                                             soup.find(id="ResultadoConsulta").find("tbody").find_all("tr") if
                                             len(x.find_all("th")) > 0]:

                            link_resultado = th_resultado.find("a")
                            if link_resultado:
                                # busca numero de paginas
                                soup2 = bs(requests.get(
                                    "http://pesquisa.in.gov.br/imprensa" + link_resultado['href'][2:]).text, "html5lib")
                                num_paginas = int(re.search('.{1,}\&totalArquivos=([0-9]{1,})',
                                                            soup2.find("frame", attrs={"name": "controlador"})[
                                                                "src"]).group(1))

                                print("... ", num_paginas, "páginas")

                                for page in range(1, num_paginas + 1):

                                    name = "TRF01_COMPLETO_{DATA}_{PAG}.pdf".format(DATA=datastr,
                                                                                    PAG="{:04d}".format(page))

                                    if not self.filemanager.ja_baixado(name, data, modo=False):
                                        link = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=20&pagina={PAG}&data={DATA}&captchafield=firistAccess".format(
                                            DATA=data.strftime("%d/%m/%Y"), PAG=page)
                                        t = DownloadTask(link, name, data)
                                        mpw.append_task(t)

                                # merge task só deve ser executada após o término dos downloads
                                mpw.wait()

                                name = "TRF01_COMPLETO_{DATA}_0001.pdf".format(DATA=datastr)
                                if not self.filemanager.ja_baixado(name, data, modo=True):  # pdf apos merge
                                    print("fazendo merge", name)
                                    mpw.append_task(MergeTask(name, data))
                                    mpw.wait()

                                    # alguma coisa esquisita está acontecendo. por algum motivo o wait anterior termina
                                    # sem que o arquivo esteja de fato consolidado, fazendo assim com que o download seja
                                    # reiniciado. por isso este wait de 30s abaixo
                                    time.sleep(30)
                                    break


                    elif re.search('Erro ao processar o arquivo PDF. Verifique o número da página e a data',
                                   pagina.text, re.I):
                        # nao há mais páginas. buscar próxima data
                        pass

                    elif pagina.status_code != 200:
                        print(" ", pagina.status_code, " status code. tentando novamente em 5 segundos")
                        time.sleep(5)
                        tentativas += 1

                    elif re.search('Nenhum registro encontrado para a pesquisa', pagina.text):
                        print(" - Não há registros para data")
                        tentativas = 3  # não será tentado já que não há páginas

                    elif re.search('Connection timed out', pagina.text):
                        # wait and retry
                        time.sleep(5)
                        tentativas += 1

                    else:
                        print("nada deu match :(")
                        tentativas = 3  # não será tentado já que não se identificou o problema
                        print(pagina.text)
                        break

        mpw.wait()
        mpw.terminate()

    def __download_trf1_antigo(self, data):

        """
            DEPRECATED - O SITE SAIU DO AR!!!

            Não encontrei os diários de 2007 a 2009 publicados em lugar nenhum

            -------------------------------------------------------------------------

            baixa os eDJF1 entre 05/10/2007 e 06/10/2009
            fonte: www.trf1.jus.br/Consulta/DiarioEletronico/DiarioEletronicoeDJF1
            form: http://pesquisa.in.gov.br/imprensa/core/consultaDjEdjf1.action
        """

        start_date = date(2007, 10, 26)  # data inicial
        end_date = date(2009, 10, 6)

        mpw = WorkManager(1)  # i/o bound process
        mpw.start_procs()
        connection_down = False

        for data in daterange(start_date, end_date):

            print(data.strftime('%d/%m/%Y'))

            for entidade in range(0, 15):

                if connection_down:
                    break

                tentativas = 0  # cada data é tentada no máximo 3x
                sucesso = False

                while tentativas < 3 and not sucesso:

                    datastr = data.strftime('%Y_%m_%d')

                    name1 = "TRF01_{ENT}_UNICO_{DATA}.pdf".format(DATA=datastr, ENT="{:02d}".format(entidade))
                    name2 = "TRF01_{ENT}_ADM_{DATA}.pdf".format(DATA=datastr, ENT="{:02d}".format(entidade))
                    name3 = "TRF01_{ENT}_JUD_{DATA}.pdf".format(DATA=datastr, ENT="{:02d}".format(entidade))

                    if self.filemanager.ja_baixado(name1, data, modo=True) \
                            or self.filemanager.ja_baixado(name2, data, modo=True) \
                            or self.filemanager.ja_baixado(name3, data, modo=True):
                        break  # buscar próxima data

                    else:
                        if entidade == 0:
                            docorigem = "PRESI - Presidência"
                            docorg = "15"
                            data_selecionada = '{DIA}/{MES}/{ANO}'.format(DIA='{:02d}'.format(data.day),
                                                                          MES='{:02d}'.format(data.month),
                                                                          ANO=data.year),
                            data_divulgacao = ""
                        else:
                            docorigem = "DIREF - Diretoria do Foro"
                            docorg = "7"
                            data_divulgacao = '{DIA}/{MES}/{ANO}'.format(DIA='{:02d}'.format(data.day),
                                                                         MES='{:02d}'.format(data.month),
                                                                         ANO=data.year),
                            data_selecionada = ""

                        params = {
                            'dataSelecionada': data_selecionada,
                            'Entidade': '10001{ENT}000000'.format(ENT="{:02d}".format(entidade)),
                            'DocOrgOrigemNome': docorigem,
                            'DocOrgOrigem': docorg,
                            'TDocNome': '217 - Diário Eletrônico',
                            'TDoc': '217',
                            'NumDoc': '',
                            'dataDivulgacao': data_divulgacao,
                            'ArgPes': ''
                        }

                        try:
                            pagina = requests.post(
                                'http://www.trf1.jus.br/Consulta/DiarioEletronico/DiarioEletronicoeDJF1.php?acao=ver',
                                data=params,
                                verify=False, timeout=self.timeout)

                        except requests.exceptions.ReadTimeout:
                            print(" Timeout... Tentando novamente")
                            tentativas += 1

                            if tentativas == 3:
                                print("Numero de tentativas esgotadas. Verificar a conexão com a internet.")
                                connection_down = True

                            continue  # volta para o inicio do loop while
                        except:
                            print(pagina.text)

                        if pagina.status_code != 200:
                            print(" ", pagina.status_code, " status code. tentando novamente em 5 segundos")
                            time.sleep(5)
                            tentativas += 1

                        elif re.search('não foi encontrado nenhum documento', pagina.text, re.I):
                            # print(" - Não há registros para data nesta entidade")
                            tentativas = 3  # não será tentado já que não há páginas

                        elif re.search('invalidada', pagina.text, re.I):
                            ConfigManager().escreve_log("edição invalidada", "TRF", "log_download_trf1-3.txt",
                                                        verbose=False)
                            tentativas = 3

                        else:  # consulta retornou resultados

                            soup = bs(pagina.text, "html5lib")
                            achou = False

                            try:
                                results = soup.find_all("table")[3].find_all("tr")[4:]
                                achou = True
                            except:
                                results = []
                                ConfigManager().escreve_log(soup.prettify(), "TRF", "log_download_trf1-3.txt",
                                                            verbose=False)

                            if achou:
                                ConfigManager().escreve_log(
                                    "Baixando diario do dia {DATA} em {ENT}".format(DATA=data.strftime("%d-%m-%Y"),
                                                                                    ENT="{:02d}".format(entidade)),
                                    "TRF", "log_download_trf1-3.txt")

                            for resultado in results:

                                link_resultado = resultado.find_all("td")[3].find("a")["href"]
                                tomo = resultado.find_all("td")[3].find("a").text
                                if re.search("ADMINISTRATIVO", tomo):
                                    tomo = "ADM"
                                elif re.search("JUDICIAL", tomo):
                                    tomo = "JUD"
                                elif re.search("ÚNICO", tomo):
                                    tomo = "UNICO"
                                else:
                                    tomo = "VERIFICAR"

                                if link_resultado:
                                    link = 'https://www.trf1.jus.br/Consulta/DiarioEletronico/DocEdjf1/{ARQ}'.format(
                                        ARQ=re.search('nomeArquivo=(.{1,}\.pdf)&', link_resultado).group(1))
                                    name = "TRF01_{ENT}_{TOMO}_{DATA}.pdf".format(DATA=datastr,
                                                                                  ENT="{:02d}".format(entidade),
                                                                                  TOMO=tomo)

                                    if not self.filemanager.ja_baixado(name, data, modo=False):
                                        t = DownloadTask(link, name, data)  # download assincrono
                                        mpw.append_task(t)

                            sucesso = True  # pagina foi baixada com sucesso

        mpw.wait()
        mpw.terminate()


if __name__ == '__main__':
    robo = RoboDiarioTRF1()
    robo.download_atualizacao_diaria(verifica_todo_periodo=False)


