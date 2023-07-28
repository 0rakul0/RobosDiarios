from datetime import datetime, date
import calendar
import os
import traceback
import requests
import re
import time
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioDEJT (RoboDiarioBase):

    def __init__(self):
        self.__url_dejt = "https://dejt.jt.jus.br/dejt/f/n/diariocon"
        self.navDe = 1
        self.viewstate = " "
        self.count = 0
        self.s = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }


        super(RoboDiarioDEJT, self).__init__("DEJT", "log_robo_dejt.txt", "erro_robo_dejt.txt")
    def download_atualizacao_diaria(self):
        self.download_trt()

    def download_trt(self):
        #Requisição para pegar o parâmetro viewState,necessário para entrar na página
        paginaPrimeiroAcesso = self.myget(self.s, self.__url_dejt,'get')
        soupPrimeiroAcesso = bs(paginaPrimeiroAcesso.text, 'html5lib')
        self.viewstate = soupPrimeiroAcesso.findAll('input', {'name': 'javax.faces.ViewState'})[1].attrs['value']
        paramsLista = {
            'corpo:formulario:dataIni': self.data_limite().strftime("%d/%m/%Y"),
            'corpo:formulario:dataFim': datetime.today().strftime("%d/%m/%Y"),
            'corpo:formulario:tipoCaderno': '',
            'corpo:formulario:tribunal': '',
            'corpo:formulario:ordenacaoPlc': '',
            'navDe': self.navDe,
            'detCorrPlc': '',
            'tabCorrPlc': '',
            'detCorrPlcPaginado': '',
            'exibeEdDocPlc': '',
            'indExcDetPlc': '',
            'org.apache.myfaces.trinidad.faces.FORM': 'corpo:formulario',
            '_noJavaScript': 'false',
            'javax.faces.ViewState': self.viewstate,
            'source': 'corpo:formulario:botaoAcaoPesquisar'
        }

        # Requisição para entrar na página dos diários
        pagina = self.myget(self.s, self.__url_dejt, 'post', paramsLista)
        soup = bs(pagina.text, 'html5lib')
        #Determina o número de páginas para navegar
        num_oc = int(re.search('[0-9]+ *?até *?[0-9]+ *?de *?([0-9]+)', soup.prettify()).group(1).strip())
        num_pag = num_oc // 30 + (0 if num_oc % 30 == 0 else 1) - 1

        #Looping em cada página
        for pg in range(num_pag):
            #Lista de diários na página
            diarios = [i.text for i in soup.find_all('td', {'class': 'campo'}) if i.text != ""]

            #For para baixar todos os diários da página. O zip() ira dividir em 2 listas. Uma com todas as datas e outra com todos os nomes
            for diario in zip(diarios[::2],diarios[1::2]):
                paramsDiario = {
                    'corpo:formulario:dataIni': self.data_limite().strftime("%d/%m/%Y"),
                    'corpo:formulario:dataFim': datetime.today().strftime("%d/%m/%Y"),
                    'corpo:formulario:tipoCaderno': '',
                    'corpo:formulario:tribunal': '',
                    'corpo:formulario:ordenacaoPlc': '',
                    'navDe': self.navDe,
                    'detCorrPlc': '',
                    'tabCorrPlc': '',
                    'detCorrPlcPaginado': '',
                    'exibeEdDocPlc': '',
                    'indExcDetPlc': '',
                    'org.apache.myfaces.trinidad.faces.FORM': 'corpo:formulario',
                    '_noJavaScript': 'false',
                    'javax.faces.ViewState': soup.findAll('input', {'name': 'javax.faces.ViewState'})[1].attrs['value'],
                    'source': 'corpo:formulario:plcLogicaItens:' + str(self.count) + ':j_id131'
                }
                #Requisição para baixar cada diário
                data_diario = datetime.strptime(diario[0], '%d/%m/%Y')
                nome_diario = remove_acentos(diario[1]).split("-")
                self.filemanager.download(name="TRT_{tipo}_{nome}_{data}.pdf".format(tipo=nome_diario[2],nome=re.sub(" ","_",nome_diario[1].strip()),data=data_diario.strftime("%Y_%m_%d")).replace(' ',''),
                                          data=data_diario,
                                          url=self.__url_dejt, session=self.s,
                                          params_post=paramsDiario)

                self.count += 1

            #Post para passar de página
            self.navDe += 30  # incrementa de 30 a 30. Necessário para passar de página
            paramsLista = {
                'corpo:formulario:botaoAcaoRecuperaPorDemanda': '',
                'corpo:formulario:botaoAcaoLimparArgs_LIMPAR_ARGS': '',
                'corpo:formulario:botaoAcaoPesquisar': '',
                'corpo:formulario:botaoRecuperaUnidadePorTribunalSelecionado': '',
                'corpo:formulario:confirma': '',
                'corpo:formulario:dataIni': self.data_limite().strftime("%d/%m/%Y"),
                'corpo:formulario:dataFim': datetime.today().strftime("%d/%m/%Y"),
                'corpo:formulario:tipoCaderno': '',
                'corpo:formulario:tribunal': '',
                'corpo:formulario:ordenacaoPlc': '',
                'navDe': self.navDe,
                'detCorrPlc': '',
                'tabCorrPlc': '',
                'detCorrPlcPaginado': '',
                'exibeEdDocPlc': '',
                'indExcDetPlc': '',
                'org.apache.myfaces.trinidad.faces.FORM': 'corpo:formulario',
                '_noJavaScript': 'false',
                'javax.faces.ViewState': soup.findAll('input', {'name': 'javax.faces.ViewState'})[1].attrs['value'],
                'event': 'autosub',
                'source': 'corpo:formulario:j_id191',
                'partial': 'true'
            }

            pagina = self.myget(self.s, self.__url_dejt, 'post', paramsLista)
            soup = bs(pagina.text, 'html5lib')

            self.count = 0 #Retorna para 0. Pois os diários vão sempre de 0 a 29 por página

    def myget(self, s, link,tipo,parametros=None):
        tentativas = 4
        conseguiu = False
        pagina = None
        while tentativas >= 0 and not conseguiu:
            try:
                if tipo=='get':
                    pagina = s.get(link,verify=False, timeout=3000,headers=self.headers)
                else:
                    pagina = s.post(link,data=parametros,timeout=3000,verify = False,headers=self.headers)
                if not pagina:
                    conseguiu = False
                else:
                    conseguiu = True
            except UnicodeDecodeError as erropagina:
                raise erropagina
            except:
                time.sleep(10)
                tentativas -= 1

        return pagina


    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return date (2015, 6, 20)


if __name__ == '__main__':
    RoboDEJT = RoboDiarioDEJT()
    RoboDEJT.download_atualizacao_diaria()