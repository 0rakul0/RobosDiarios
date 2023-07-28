# -*- coding: utf-8 -*-
import sys
import importlib, re, os

from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.DiarioService import DiarioService
from util.ConfigManager import ConfigManager
from datetime import datetime
importlib.reload(sys)
import abc

from util.FileManager import FileManager, MaxTentativasExcedidas, MaxTentativasCaptchas


class RoboDiarioBase(object, metaclass=abc.ABCMeta):
    def __init__(self, robo, log, erro):
        self.__robo = robo
        self.__log = log
        self.__erro = erro
        self.__filemanager = FileManager(robo, log, erro)
        self.__timeout = self.__filemanager.timeout
        self.__tentativas = 0
        self.__tentativas_captcha = 0

    @property
    def robo(self):
        return self.__robo

    @property
    def log(self):
        return self.__log

    @property
    def erro(self):
        return self.__erro

    @property
    def filemanager(self):
        return self.__filemanager

    @property
    def max_tentativas(self):
        return 10

    @property
    def max_captchas(self):
        return 30

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        self.__timeout = value

    @property
    def tentativas(self):
        return self.__tentativas

    @tentativas.setter
    def tentativas(self, value):
        if value < self.max_tentativas:
            self.__tentativas = value
        else:
            erro = "Máximo de tentativas de acesso a URL feitas por {robo}".format(
                robo=self.__robo)

            ConfigManager().escreve_log("Erro: {e}".format(e=erro), self.__robo, self.__erro)
            raise MaxTentativasExcedidas(erro)

    @property
    def tentativas_captcha(self):
        return self.__tentativas_captcha

    @tentativas_captcha.setter
    def tentativas_captcha(self, value):
        if value < self.max_captchas:
            self.__tentativas_captcha = value
        else:
            erro = "Máximo de tentativas de solução do captcha feitos por {robo}.".format(
                robo=self.__robo)

            ConfigManager().escreve_log("Erro: {e}".format(e=erro), self.__robo, self.__log)
            raise MaxTentativasCaptchas(erro)

    def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True, subfolders=None):

        ultimo = self.__filemanager.data_ultimo_arquivo(filtro, tipo_arquivo, por_tipo, subfolders)
        return ultimo.date() if ultimo is not None else self.data_limite()

    @abc.abstractmethod
    def download_atualizacao_diaria(self):
        return

    @abc.abstractmethod
    def data_limite(self):
        return

    def verificar_pdf(self, arq):
        return self.filemanager.verificar_pdf(arq)

    def inserir_no_banco_para_extrair(self, nome_arquivo,contagem_separador=0,formato_arquivo='txt'):
        # A contagem_separador serve para pegar o nome do diario até a n-ésima vez que um caracter aparece.
        #Por exemplo TRF03_ATA_DISTRIB_5_2009_07_06.pdf, se eu colocar contagem_separador = 2, ele vai me entregar
        # TRF03_ATA_DISTRIB. Caso não coloque nada (0) ele retorna TRF03
        diario_service = DiarioService()
        arquivo_service = ArquivoService()
        nome_diario = nome_arquivo[:nome_arquivo.replace('_','X',contagem_separador).find('_')]
        data_diario = re.search('(\d{4}_\d{2}_\d{2})\.'+formato_arquivo,nome_arquivo)
        if data_diario:
            data = datetime.strptime(data_diario.group(1),'%Y_%m_%d')
        else:
            data = None

        diario = diario_service.preenche_diario(nome_diario, data)

        arquivo= arquivo_service.preenche_arquivo(nome_arquivo,diario,status_baixado=datetime.now())

    def inserir_no_banco_como_baixado(self, nome_arquivo,contagem_separador=0,formato_arquivo='txt'):
        diario_service = DiarioService()
        arquivo_service = ArquivoService()
        nome_diario = nome_arquivo[:nome_arquivo.replace('_','X',contagem_separador).find('_')]
        data_diario = re.search('(\d{4}_\d{2}_\d{2})\.'+formato_arquivo,nome_arquivo)
        if data_diario:
            data = datetime.strptime(data_diario.group(1),'%Y_%m_%d')
        else:
            data = None

        diario = diario_service.preenche_diario(nome_diario, data)

        arquivo= arquivo_service.preenche_arquivo(nome_arquivo,diario,status_baixado = datetime.now())


