import requests
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.Endereco import Endereco
from pdjus.modelo.Estado import Estado
from pdjus.modelo.Reparticao import Reparticao
from pdjus.modelo.ReparticaoSegundoGrau import ReparticaoSegundoGrau
from pdjus.service.ValorDiarioService import ValorDiarioService
from util.StringUtil import remove_sub_str
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from datetime import date, timedelta, datetime
import re
from bs4 import BeautifulSoup as bs


class RoboDiarioValor(RoboDiarioBase):

    def __init__(self):
        self.url = "http://www.valor.com.br/"
        self.url_login = "http://www.valor.com.br/login"
        self.usuario = ""
        self.senha = ""
        self.url_busca_movimento_falimentar = 'http://www.valor.com.br/search/apachesolr_search/movimento-falimentar?page={pagina}&filters=created%3A[{ano-limite}-{mes_limite:02d}-{dia_limite:02d}T00%3A00%3A00Z%20TO%20{ano_atual}-{mes_atual:02d}-{dia_amanha:02d}T00%3A00%3A00Z]%20-type%3Avalor_international_conteudo%20-type%3Awall_street_journal%20-type%3Avalor_ri*%20-channel%3Ari&solrsort=created%20desc'#.format(pagina,ano_limite,mes_limite,dia_limite,ano_atual,mes_atual,dia_atual)
        self.session = None
        super(RoboDiarioValor, self).__init__("RoboDiarioValor", "log_robo_valor.txt", "erro_robo_valor.txt")

    def download_atualizacao_diaria(self):
        pass

    def data_mais_recente(self):
        data = ValorDiarioService().dao.get_data_mais_recente()
        if data:
            return data
        return self.data_limite()

    def busca_paginas_movimento_falimentar(self):
        pilha_links = []

        expressao_data = re.compile('\d{2}\/\d{2}\/\d{4}')
        data_mais_recente = self.data_mais_recente()
        data_amanha = date.today() + timedelta(days=1)
        datas_menores_ou_fora_de_ordem = 0 #usado para que toda vez que tenha uma data fora de ordem ou mais antiga do
        #  que o que já coletamos, ele incremente. Chegando em 10 para. Isso foi feito porque existem datas que podem
        #  estar fora de ordem
        self.logar()
        next_page = self.url_busca_movimento_falimentar.format(0,data_mais_recente.year,data_mais_recente.month,
                                                                           data_mais_recente.day,data_amanha.year,data_amanha.month,
                                                                           data_amanha.day)
        possui_proxima_pagina = True
        while possui_proxima_pagina:
            dado = self.session.get(next_page, verify=False, timeout=self.timeout)
            htm = dado.content
            soup = bs(htm,"html5lib")
            resultados = soup.find_all('div', {'class' : 'group search-result-item search-result search-item-noticia_impresso'})
            for resultado in resultados:
                data_span = resultado.find('span',{'class': 'date'}).get_text().strip()
                data_match = expressao_data.search(data_span)
                if data_match:
                    data_resultado = datetime.strptime(data_match.group(1),'%d/%m/%Y').date()
                else:
                    data_resultado = date.today()
                if data_resultado > data_mais_recente:
                    pilha_links.insert(0,resultado.find('a')['href'])
                else:
                    datas_menores_ou_fora_de_ordem += 1
            next_page = soup.find('li', {'class' : 'pager-next'}).find('a')['href']
            possui_proxima_pagina = ((next_page is not None) and datas_menores_ou_fora_de_ordem<10)

        for link in pilha_links:
            self.visita_pagina(link)



    def visita_pagina(self, url_pagina):
        expressao_data = re.compile('\d{2}\/\d{2}\/\d{4}') #falta pegar data e passar para os métodos de pegar dados
        dado = self.session.get(url_pagina, verify=False, timeout=self.timeout)
        htm = dado.content
        soup = bs(htm,"html5lib")
        body = soup.find('div', {'class' : 'n-content'})
        linhas = body.findChildren()
        titulo = ''
        for linha in linhas:
            if linha.name == 'h3':
                titulo = linha.get_text()
            if linha.name == 'p':
                if titulo:
                    if titulo.lower() in ['falências requeridas','processos de falência extintos']:
                        self.pega_dados_falencia_requerida_ou_extinta(linha.get_text, titulo)
                    elif titulo.lower() in ['recuperação judicial requerida', 'recuperação judicial deferida',
                                            'falências decretadas', 'recuperação judicial indeferida',
                                            'cumprimento de recuperação judicial', 'recuperações judiciais concedidas']:
                        self.pega_dados_empresa(linha,titulo)
                    else:
                        ConfigManager().escreve_log("Título não previsto: '{}'".format(titulo), self.robo, self.erro)
                else:
                    ConfigManager().escreve_log("Título não encontrado", self.robo, self.erro)

    def logar(self):
        data = {"mail":self.usuario,"pass":self.senha}
        self.session = requests.Session()
        self.session.post(self.url_login,data=data)

    #PARADO, FALTA CRIAR OS OBJETOS, INSERIR... ABANDONADO POR AQUI
    def pega_dados_falencia_requerida_ou_extinta(self,linha, situacao):
        # REGEX devem ser feitos nesta ordem para não dar erro por causa que são subconjuntos um do outro
        expressao_requerida_completa = re.compile('Requerido: *(.*) *- *CNPJ: *(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}) *- *Endereço: *(.*) *- *Requerente: *(.*) *- *Vara\/Comarca: *(.*)\/(\w{2})')

        expressao_requerida_sem_endereco = re.compile('Requerido: *(.*) *- *CNPJ: *(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}) *- *Requerente: *(.*) *- *Vara\/Comarca: *(.*)\/(\w{2})')

        expressao_requerida_sem_cnpj = re.compile('Requerido: *(.*) *- *Endereço: *(.*) *- *Requerente: *(.*) *- *Vara\/Comarca: *(.*)\/(\w{2})')

        expressao_requerida_sem_cnpj_sem_endereco = re.compile('Requerido: *(.*) *- *Requerente: *(.*) *- *Vara\/Comarca: *(.*)\/(\w{2})')

        exp_completa_match = expressao_requerida_completa.search(linha,re.IGNORECASE)
        if exp_completa_match:
            nome_empresa = exp_completa_match.group(1)
            cnpj = exp_completa_match.group(2)
            desc_endereco = exp_completa_match.group(3)
            requerente = exp_completa_match.group(4)
            desc_vara = exp_completa_match.group(5)
            desc_estado = exp_completa_match.group(6).strip()[:2]
            empresa_requerida = self.get_empresa(nome_empresa,cnpj)
            endereco = self.get_endereco(desc_endereco)
            vara = self.get_reparticao(desc_vara)
            empresa_requerente = self.get_empresa(requerente)
            estado = self.get_estado(desc_estado)
            # group(1) requerido, group(2) cnpj, group(3): endereço, group(4): requerente, group(5) vara/comarca, group(6) estado em sigla, pode haver coisas além como observação... deve ter que dar split e strip
        else:
            exp_sem_endereco_match = expressao_requerida_sem_endereco.search(linha)
            if exp_sem_endereco_match:
                nome_empresa = exp_completa_match.group(1)
                cnpj = exp_completa_match.group(2)
                requerente = exp_completa_match.group(3)
                desc_vara = exp_completa_match.group(4)
                desc_estado = exp_completa_match.group(5).strip()[:2]
                empresa_requerida = self.get_empresa(nome_empresa,cnpj)
                vara = self.get_reparticao(desc_vara)
                empresa_requerente = self.get_empresa(requerente)
                estado = self.get_estado(desc_estado)
                # group(1) requerido, group(2) cnpj, group3: requerente, group(4) vara/comarca, group(5) estado em sigla, pode haver coisas além como observação... deve ter que dar split e strip
            else:
                exp_sem_cnpj_match = expressao_requerida_sem_cnpj.search(linha)
                if exp_sem_cnpj_match:
                    nome_empresa = exp_completa_match.group(1)
                    desc_endereco = exp_completa_match.group(2)
                    requerente = exp_completa_match.group(3)
                    desc_vara = exp_completa_match.group(4)
                    desc_estado = exp_completa_match.group(5).strip()[:2]
                    empresa_requerida = self.get_empresa(nome_empresa)
                    endereco = self.get_endereco(desc_endereco)
                    vara = self.get_reparticao(desc_vara)
                    empresa_requerente = self.get_empresa(requerente)
                    estado = self.get_estado(desc_estado)
                    # group(1) requerido, group(2) endereço, group(3) requerente, group(4) vara/comarca, group(5) estado em sigla, pode haver coisas além como observação... deve ter que dar split e strip
                else:
                    exp_sem_cnpj_sem_endereco_match = expressao_requerida_sem_cnpj_sem_endereco.search(linha)
                    if exp_sem_cnpj_sem_endereco_match:
                        nome_empresa = exp_completa_match.group(1)
                        requerente = exp_completa_match.group(2)
                        desc_vara = exp_completa_match.group(3)
                        desc_estado = exp_completa_match.group(4).strip()[:2]
                        empresa_requerida = self.get_empresa(nome_empresa)
                        vara = self.get_reparticao(desc_vara)
                        empresa_requerente = self.get_empresa(requerente)
                        estado = self.get_estado(desc_estado)
                        # group(1) requerido, group(2) requerente, group(3) vara/comarca, group(4) estado em sigla, pode haver coisas além como observação... deve ter que dar split e strip
                    else:
                        ConfigManager().escreve_log("Não teve match em pega_dados_falencia_requerida_ou_extinta com o título {} e a  linha: {}".format(situacao,linha), self.robo, self.erro)

    def pega_dados_empresa(self,linha,situacao):
        # REGEX devem ser feitos nesta ordem para não dar erro por causa que são subconjuntos um do outro
        expressao_empresa_completa = re.compile('empresa:(.*)- *cnpj: *(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}) *- *Endere[çc]o:(.*) *- *Administrador Judicial:(.*) *- *vara\/comarca:(.*)\/(\w{2})')

        expressao_empresa_sem_administrador = re.compile('empresa:(.*)- *cnpj: *(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}) *- *Endere[çc]o:(.*) *- *vara\/comarca:(.*)\/(\w{2})')

        exp_completa_match = expressao_empresa_completa.search(linha,re.IGNORECASE)
        if exp_completa_match:
           nome_empresa = exp_completa_match.group(1)
           cnpj = exp_completa_match.group(2)
           desc_endereco = exp_completa_match.group(3)
           desc_reparticao = exp_completa_match.group(5)
           desc_estado = exp_completa_match.group(6)
           empresa = self.get_empresa(nome_empresa,cnpj)
           endereco = self.get_endereco(desc_endereco)
           reparticao = self.get_reparticao(desc_reparticao)
           estado = self.get_estado(desc_estado)
        else:
            exp_sem_administrador_match = expressao_empresa_sem_administrador.search(linha)
            if exp_sem_administrador_match:
                nome_empresa = exp_completa_match.group(1)
                cnpj = exp_completa_match.group(2)
                desc_endereco = exp_completa_match.group(3)
                desc_reparticao = exp_completa_match.group(5)
                desc_estado = exp_completa_match.group(6)
                empresa = self.get_empresa(nome_empresa,cnpj)
                endereco = self.get_endereco(desc_endereco)
                reparticao = self.get_reparticao(desc_reparticao)
                estado = self.get_estado(desc_estado)
            else:
                ConfigManager().escreve_log("Não teve match em pega_dados_empresa com o título {} e a linha: {}".format(situacao, linha), self.robo, self.erro)

    def get_endereco(self, desc_endereco):
        endereco = Endereco()

        try:
            numero = re.search("\,(( *)?)((\d)*)(( *)?)(\,)?",desc_endereco).group(3)
            desc_endereco = remove_sub_str(desc_endereco,numero)
        except Exception:
            numero = ""

        try:
            complemento = re.search("\,(.*)\,(.*)",desc_endereco).group(1)
            cidade = re.search("\,(.*)\,(.*)",desc_endereco).group(2)
            desc_endereco = remove_sub_str(desc_endereco,complemento)
            desc_endereco = remove_sub_str(desc_endereco,cidade)
        except Exception:
            complemento = ""
            cidade = ""

        rua = desc_endereco
        if rua:
            endereco.rua = rua
            if numero:
                endereco.numero = numero
            if complemento:
                endereco.complemento = complemento
        if cidade:
            endereco.cidade = cidade

        return endereco


    def get_empresa(self, nome_empresa, cnpj=None):
        empresa = Empresa()
        empresa.nome = nome_empresa
        empresa.cnpj = cnpj

        return empresa

    def get_reparticao(self, desc_reparticao):
        if "vara" in desc_reparticao.lower():
            reparticao = Reparticao()
        else:
            reparticao = ReparticaoSegundoGrau()
        reparticao.nome = desc_reparticao

        return reparticao

    def get_estado(self, desc_estado):
        estado = Estado()
        estado.sigla = desc_estado

        return estado

    def data_limite(self):
        return date(2009, 9, 2)

if __name__ == '__main__':
    robo = RoboDiarioValor()
    robo.download_atualizacao_diaria()