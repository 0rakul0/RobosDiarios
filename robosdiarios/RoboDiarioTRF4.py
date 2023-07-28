from datetime import datetime, date
import calendar
import os
import traceback
import requests
import re
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel

#TODO: ROBÔ OK
class RoboDiarioTRF4 (RoboDiarioBase):
    """
    Robo responsavel pelo download de diarios oficias do TRF2.
    """
    def __init__(self):
        self.__url_trf4 = "https://www.trf4.jus.br/trf4/diario/edicoes_anteriores.php"
        super (RoboDiarioTRF4, self).__init__ ("TRF04", "TRF4_robodiario.txt", "TRF4_robodiario.err")



    def download_atualizacao_diaria(self):
        """
        Aciona o metodo de download de diarios oficiais a partir de uma data definida.
        """
        self.download_trf4()

    def download_trf4(self):
        """
        Realiza o download dos diarios para as datas definidas.
        """
        tentativas = 0
        sucesso = False

        try:
            ConfigManager().escreve_log("TRF 4ª região...", self.robo, self.log)

            edicoes = ("Publicacoes_Judiciais", "Publicacoes_Administrativas")

            atual = datetime.now ().date ()  # replace(day=1)
            data = atual
            # print(data)

            for nome in edicoes:
                diario = "TRF04_{nome}".format(nome=remove_acentos (remove_varios_espacos (nome)).replace (" ", "_"))
                # print(diario)

                dt_diario = self.data_inicial(diario, somente_inicio_mes=True)  # Por enquanto está pegando a partir de date(2009, 1, 1); somente_inicio_mes=True
                # dt_diario = date(2017, 5, 1)
                print (dt_diario)

                if dt_diario <= data:
                    data = dt_diario
                    # print(data)

            while data <= atual:
                sucesso = False
                tentativas = 0

                while not sucesso and tentativas < self.max_tentativas:
                    try:
                        option = data.strftime ("%Y_%m_%d")
                        params = {'edAnteriores': option[:-3]}
                        request = requests.post (self.__url_trf4, data=params)
                        soup = bs (request.text, "html5lib")

                        form = soup.findAll ("form", {"name": "form"})

                        if len (form) > 0:
                            links_mes = form[0].findAll ("a")
                            # print(links_mes)

                            if len (links_mes) > 0:
                                for link_dia in links_mes:
                                    data_caderno = datetime.strptime (
                                        re.search ('([0-9]){2}/([0-9]){2}/([0-9]){4}', link_dia.text).group (0),
                                        "%d/%m/%Y")
                                    # print(link_dia.text)
                                    numero_caderno = link_dia.text.split (" ")[-4:]
                                    numero_caderno = numero_caderno[-1]
                                    numero_caderno = '{:04d}'.format (int (numero_caderno))
                                    # print(numero_caderno)

                                    url = "https://www.trf4.jus.br/trf4/diario/" + link_dia["href"]

                                    caderno = remove_acentos (remove_varios_espacos (edicoes[0])).replace (' ', '_') \
                                        if url.split ("_")[1] == 'jud' \
                                        else remove_acentos (remove_varios_espacos (edicoes[1])).replace (' ', '_')

                                    name = "TRF04_{tipo}_{numero}_{data}.pdf".format (
                                        data=data_caderno.strftime ("%Y_%m_%d"), tipo=caderno, numero=numero_caderno)

                                    print (name + " - " + url)

                                    try:
                                        self.filemanager.download (name, data_caderno, url)  # HERE!
                                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                                        ConfigManager ().escreve_log ("Diario não disponível na data {data}".format (
                                            data=data.strftime ("%d/%m/%Y")), self.robo, self.log)

                        sucesso = True
                        tentativas = 0


                    except Exception as e:
                        ConfigManager ().escreve_log (
                            "Erro ao acessar {url}. Tentativa {t}... Detalhes: {erro}".format (
                                url=self.__url_trf4,
                                t=str (tentativas),
                                erro=str (e)), self.robo, self.erro)

                        tentativas += 1
                if sucesso:
                    ConfigManager ().escreve_log ("Diários de {data} baixados.".format (data=data.strftime ("%m/%Y")),
                                                  self.robo, self.log)
                else:
                    ConfigManager ().escreve_log (
                        "Erro ao baixar diários de {data}.".format (data=data.strftime ("%m/%Y")),
                        self.robo, self.erro)

                data = self.__add_months (data, 1)

        except Exception as e:
            ConfigManager ().escreve_log ("Erro ao acessar página principal: " + traceback.format_exc (), self.robo,
                                          self.erro)
            tentativas += 1


    def escreve_log(self, txt):
        ConfigManager ().escreve_log (txt, self.robo, self.log, verbose=False)


    def move_arquivos(self, pasta):
        """
        Move diarios baixados para pasta correta.
        """
        arquivos = os.listdir (pasta)
        for arquivo in arquivos:
            nome = self.novo_nome (arquivo)
            if nome:
                try:
                    os.rename (os.path.join (pasta, arquivo), os.path.join (
                        self.filemanager.caminho (arquivo, self.filemanager.obter_data (arquivo)), nome))
                except Exception as e:
                    pass

    def novo_nome(self, antigo):
        """
        Renomeia diarios para seguir o padrao estabelecido.
        """
        if not "TRF2" in antigo or ".part" in antigo:
            return None
        regex = re.search ("(\d{2}\d{2}\d{4})_.*_(.*)\.(.*)", antigo)
        data = datetime.strptime (regex.group (1), "%d%m%Y").date ()
        caderno = regex.group (2)
        extensao = regex.group (3)
        if data and caderno and extensao:
            novo = "TRF02_" + caderno + "_" + data.strftime ("%Y_%m_%d") + "." + extensao
        else:
            novo = None
        return novo

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
        data = super (RoboDiarioTRF4, self).data_inicial (filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace (day=1)

        return data

    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return date (2017, 6, 23)

if __name__ == '__main__':
    RoboTRF4 = RoboDiarioTRF4()
    RoboTRF4.download_atualizacao_diaria()
