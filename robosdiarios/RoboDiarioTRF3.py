from datetime import datetime, date
import calendar
import os, shutil
import traceback
import requests
import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from pdjus.conexao.Conexao import default_schema
from util.DateUtil import parse_mes_para_num

class RoboDiarioTRF3(RoboDiarioBase):
    """
    Robo responsavel pelo download de diarios oficias do TRF3.
    """
    def __init__(self):
        self.url_trf3 = "http://web.trf3.jus.br/diario/Consulta/PublicacoesAnteriores/{data}"
        self.url_atas_distrib_trf3 = "http://web.trf3.jus.br/atasdistribuicao/Ata/ListarDados/{}"
        # self.proxies = {'http': 'cache.ipea.gov.br:3128'}
        self.s = requests.Session()
        super (RoboDiarioTRF3, self).__init__ ("TRF03", "TRF3_robodiario.txt", "TRF3_robodiario.err")

    def download_atualizacao_diaria(self):
        self.donwload_atas_distribuicao_trf3 ()
        self.download_trf3 ()

    def escreve_log(self, texto):
        ConfigManager ().escreve_log (texto, self.robo, self.log)

    def download_trf3(self):
        """
        Realiza o download dos diarios para as datas definidas.
        """
        tentativas = 0
        sucesso = False

        try:

            edicoes = (
            "Publicacoes_Administrativas", "Publicacoes_Judiciais_I_-_TRF", "Publicacoes_Judiciais_II_-_TRF",
            "Publicacoes_Judiciais_I_-_Capital_SP", "Publicacoes_Judiciais_II_-_Capital_SP",
            "Publicacoes_Judiciais_I_-_Interior_SP_e_MS", "Publicacoes_Judiciais_II_-_Interior_SP_e_MS",
            "Publicacoes_Judiciais_I_-_JEF", "Publicacoes_Judiciais_II_-_JEF")

            atual = datetime.now ().date ()
            data = atual

            for nome in edicoes:
                diario = "TRF03_{nome}".format (
                    nome=remove_acentos (remove_varios_espacos (nome)).replace (" ", "_"))

                dt_diario = self.data_inicial (diario, somente_inicio_mes=True)

                if dt_diario < data:
                    data = dt_diario

            while data <= atual:
                self.escreve_log('+-+-+-+ ' + str (datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")) + ' +-+-+-+')
                sucesso = False
                tentativas = 0

                while not sucesso and tentativas < self.max_tentativas:
                    try:
                        res = Request(self.url_trf3.format(data=data.strftime("%Y-%m-%d")))
                        html = urlopen(res)

                        soup = bs(html.read(), "html5lib")
                        divs = soup.findAll("div", {"id": "conteudoPrincipal"})

                        if len(divs) > 0:
                            conteudo = divs[0].findChildren ()[2]

                            for div in conteudo.findAll ("div"):
                                tags = div.findAll ("b")
                                links = div.findAll ("a")

                                if len (tags) > 0 and len (links) > 0:
                                    caderno = remove_acentos (remove_varios_espacos (tags[0].text)).replace (' ', '_')

                                    for link in links:
                                        data_caderno = datetime.strptime (
                                            re.search ('([0-9]){2}/([0-9]){2}/([0-9]){4}', link.text).group (0),
                                            "%d/%m/%Y")
                                        url = "http://web.trf3.jus.br" + link["href"]

                                        name = "TRF03_{tipo}_{data}.pdf".format (
                                            data=data_caderno.strftime ("%Y_%m_%d"), tipo=caderno)

                                        try:
                                            self.filemanager.download_urlopen (name, data_caderno, url)
                                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                                            ConfigManager ().escreve_log (
                                                "Diario não disponível na data {data}".format (
                                                    data=data.strftime ("%d/%m/%Y")), self.robo, self.log)

                            sucesso = True
                            tentativas = 0
                        else:
                            ConfigManager ().escreve_log (
                                "Sem diários no dia {data}. Prosseguindo...".format (
                                    data=data.strftime ("%d/%m/%Y")),
                                self.robo, self.log)
                            sucesso = True
                            tentativas = 0
                    except Exception as e:
                        ConfigManager ().escreve_log (
                            "Erro ao acessar {url}. Tentativa {t}... Detalhes: {erro}".format (
                                url=self.url_trf3.format (data=data.strftime ("%Y-%m-%d")),
                                t=str (tentativas),
                                erro=str (e)), self.robo, self.erro)
                        tentativas += 1

                if sucesso:
                    ConfigManager ().escreve_log (
                        "Diários de {data} baixados.".format (data=data.strftime ("%m/%Y")),
                        self.robo, self.log)
                else:
                    ConfigManager ().escreve_log (
                        "Erro ao baixar diários de {data}.".format (data=data.strftime ("%m/%Y")), self.robo,
                        self.erro)

                data = self.__add_months (data, 1)

        except Exception as e:
            ConfigManager ().escreve_log ("Erro ao acessar página principal: " + traceback.format_exc (), self.robo,
                                            self.erro)
            tentativas += 1


    # def move_arquivos_subfolders(self, pasta, subfolders):
    #     """
    #     Move arquivos para uma subpasta criada.
    #     """
    #     arquivos = os.listdir (pasta)
    #     for arquivo in arquivos:
    #         try:
    #             # print(os.path.join(pasta, arquivo))
    #             # print(os.path.abspath(self.filemanager.caminho(arquivo, self.filemanager.obter_data(arquivo),subfolders=subfolders)))
    #             shutil.move (os.path.join (pasta, arquivo), os.path.abspath (
    #                 self.filemanager.caminho (arquivo, self.filemanager.obter_data (arquivo))))
    #         except Exception as e:
    #             pass
    #
    # def esvazia_pasta(self, path_pasta):
    #     """
    #     Remove os aquivos de uma pasta.
    #     """
    #     for file in os.listdir (path_pasta):
    #         file_path = os.path.join (path_pasta, file)
    #         try:
    #             if os.path.isfile (file_path):
    #                 os.unlink (file_path)
    #                 # elif os.path.isdir(file_path): shutil.rmtree(file_path)
    #         except Exception as e:
    #             print (e)

    def donwload_atas_distribuicao_trf3(self):
        """
        Realiza o download das atas de distribuição.
        """
        realiza_download = True
        expressao_ata_data = re.compile ('Ata\sde\s(.*?)\sde\s(\d+)\sde\s(.*?)\sde\s(\d+)', re.IGNORECASE)
        mais_recente = self.filemanager.ultimo_arquivo ('TRF03_ATA', tipo_arquivo="*.html")
        if mais_recente:
            ultimo = int (mais_recente.split ('_')[3])
        else:
            ultimo = 1
        while realiza_download:
            # url = self.url_atas_distrib_trf3.format (ultimo)

            res = Request(self.url_atas_distrib_trf3.format (str(ultimo)))
            html = urlopen(res)
            soup = bs(html.read(), "html5lib", from_encoding='utf-8')
            if "Ata de " in soup.prettify ():
                nome_ata = re.sub (" +", ' ',
                                    soup.find ('div', {'id': 'divConteudoAtaDistribuicao'}).get_text ().replace (
                                        '\n',
                                        '')).strip ()
                match_nome_ata = expressao_ata_data.search (nome_ata)
                if match_nome_ata:
                    name = "TRF03_ATA_{nome}_{numero}_{ano}_{mes:02d}_{dia:02d}.html" \
                        .format (nome=match_nome_ata.group (1)[:5].upper (),
                                    numero=ultimo,
                                    ano=int (match_nome_ata.group (4)),
                                    mes=parse_mes_para_num (match_nome_ata.group (3)),
                                    dia=int (match_nome_ata.group (2)))
                    saida = os.path.join (self.filemanager.caminho (name), name)
                    lista_linhas_ata = []
                    ata = soup.find_all('div',{'id':'conteudo'})
                    linhas_ata = ata[0].find_all('p')
                    for linha_ata in linhas_ata:
                        lista_linhas_ata.append(linha_ata.text)

                    if not os.path.isfile(saida):
                        # html = html.read().decode('utf-8','ignore')
                        f = open(saida, 'w')
                        for linha in lista_linhas_ata:
                            f.write(linha)
                            f.flush()
                            f.write('\n')
                        f.close()
                        # self.inserir_no_banco_para_extrair (name, formato_arquivo='html')
                        if 'producao' in default_schema:
                            self.filemanager.preenche_csv_arquivo_baixado (name)
                        self.escreve_log("Arquivo {} baixado".format (name))
                    else:
                        self.escreve_log("Arquivo {} já existe. Pulando...".format (name))
            else:
                realiza_download = False

            ultimo += 1

    # def move_arquivos(self, pasta):
    #     """
    #     Move diarios baixados para pasta correta.
    #     """
    #     arquivos = os.listdir (pasta)
    #     for arquivo in arquivos:
    #         nome = self.novo_nome (arquivo)
    #         if nome:
    #             try:
    #                 os.rename (os.path.join (pasta, arquivo), os.path.join (
    #                     self.filemanager.caminho (arquivo, self.filemanager.obter_data (arquivo)), nome))
    #             except Exception as e:
    #                 pass
    #
    # def novo_nome(self, antigo):
    #     """
    #     Renomeia diarios para seguir o padrao estabelecido.
    #     """
    #     if not "TRF2" in antigo or ".part" in antigo:
    #         return None
    #     regex = re.search ("(\d{2}\d{2}\d{4})_.*_(.*)\.(.*)", antigo)
    #     data = datetime.strptime (regex.group (1), "%d%m%Y").date ()
    #     caderno = regex.group (2)
    #     extensao = regex.group (3)
    #     if data and caderno and extensao:
    #         novo = "TRF02_" + caderno + "_" + data.strftime ("%Y_%m_%d") + "." + extensao
    #     else:
    #         novo = None
    #     return novo

    def __add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int (sourcedate.year + month // 12)
        month = month % 12 + 1
        day = min (sourcedate.day, calendar.monthrange (year, month)[1])
        return date (year, month, day)

    def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True, somente_inicio_mes=False, subfolders=None):
        """
        Retorna a data do ultimo diario baixado.
        """
        data = super(RoboDiarioTRF3, self).data_inicial(filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace (day=1)

        return data

    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return date (2017, 12, 1)

if __name__ == '__main__':

    roboTRF3 = RoboDiarioTRF3()
    print ('########### INÍCIO TRF03 ###########')
    roboTRF3.download_trf3()
    roboTRF3.download_atualizacao_diaria()
    print ('########### FIM TRF03 ###########')
