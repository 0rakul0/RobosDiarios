# -*- coding: utf-8 -*-
from datetime import datetime

import os, sys, re
from pdjus.conexao.Conexao import default_schema
from pdjus.modelo.StatusExtraido import StatusExtraido
from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.ExtratorService import ExtratorService
from pdjus.service.StatusExtraidoService import StatusExtraidoService
from util.ConfigManager import ConfigManager
from util.FileManager import FileManager


class ProcessaExtrator:

    def __init__(self, robo, filetype, extrator, acompanhamento=None):
        self.__robo = robo
        self.__extrator = extrator
        self.__acompanhamento = acompanhamento
        self.__filetype = filetype
        self.__log = "log_extrator.txt"
        self.__erro = "erro_extrator.txt"
        self.__filemanager = FileManager(self.__robo, self.__log, self.__erro)

    def set_arquivo_extraido(self, arquivo, extrator,tag=None):
        status_extraido_service = StatusExtraidoService()
        status_extraido_service.preenche_status_extraido(arquivo,extrator,tag=tag)

    def extrai_arquivo(self, nome, subfolders=None, extrai_extraido=True):

        arquivo_service = ArquivoService()
        extrator_service = ExtratorService()
        status_extraido_service = StatusExtraidoService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)

        arquivo = arquivo_service.dao.get_por_nome_arquivo(nome)

        ja_extraido = status_extraido_service.is_arquivo_extraido(arquivo, extrator)

        if arquivo and (extrai_extraido or not ja_extraido):
            data = self.__filemanager.obter_data(arquivo.nome_arquivo)
            caminho_pasta = self.__filemanager.caminho(arquivo.nome_extracao, data, subfolders=subfolders)

            caminho_arquivo = os.path.join(caminho_pasta, arquivo.nome_extracao)

            arq = None
            #arq2 = None
            extraiu = False

            if os.path.isfile(caminho_arquivo):
                arq = open(caminho_arquivo, encoding='utf-8', mode='r')

            if arq:
                extraiu = self.inicia_extrator(arq, arquivo)

            if extraiu:
                # if 'producao' in default_schema:
                #     self.__filemanager.preenche_csv_arquivo_extraido(os.path.splitext(arquivo.nome_arquivo)[0])
                self.set_arquivo_extraido(arquivo, extrator)
            else:
                print(caminho_arquivo)
                raise Exception


    def inicia_extrator(self, arq, arquivo, tag=None):
        if self.__acompanhamento:
            ext = self.__extrator(arq, self.__acompanhamento(), arquivo_bd=arquivo)
            if tag:
                extraiu = ext.extrai(tag)
            else:
                extraiu = ext.extrai()

        else:
            ext = self.__extrator(arq, arquivo_bd=arquivo)
            if tag:
                extraiu = ext.extrai(tag)
            else:
                extraiu = ext.extrai()

        if not extraiu:
            print(ext._arquivo.name)

        return extraiu

    def lista_arquivos_nao_processados(self, diario):

        arquivo_service = ArquivoService()
        extrator_service = ExtratorService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)

        arquivos_totais = arquivo_service.dao.get_arquivos_nao_extraidos(extrator, diario)

        for arquivo in arquivos_totais:
            sys.stdout.write(arquivo.nome_arquivo + "\n")

    #@profile
    def extrai_diversos(self, padrao=None,tag=None,rank=0 , fatia = 1):
        arquivo_service = ArquivoService()
        extrator_service = ExtratorService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)
        arquivos_totais = arquivo_service.dao.get_arquivos_nao_extraidos(extrator,self.__extrator.nome_diario,rank=rank,fatia=fatia)
        self._realiza_extracao_de_arquivos(arquivos_totais, extrator, padrao, tag)
    # @profile
    def extrai_diversos_diretorio(self, diretorio, padrao,tag=None):

        extrator_service = ExtratorService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)

        arquivos = [f for f in sorted(os.listdir(diretorio)) if re.search(padrao,f)]

        for arquivo in arquivos:

            caminho_arquivo = os.path.join(diretorio, arquivo)

            with open(caminho_arquivo, encoding='utf-8', mode='r', errors="ignore") as arq:
                extraiu = self.inicia_extrator(arq, arquivo,tag)

            if extraiu:
                if'producao' in default_schema:
                    self.__filemanager.preenche_csv_arquivo_extraido(os.path.splitext(arquivo)[0])
                self.set_arquivo_extraido(arquivo, extrator,tag)

    def _realiza_extracao_de_arquivos(self, arquivos_totais, extrator, padrao, tag= None):
        if padrao:
            arquivos = [f for f in arquivos_totais if re.search(padrao,f.nome_extracao)]
        else:
            arquivos = arquivos_totais
        for arquivo in arquivos:

            data = self.__filemanager.obter_data(arquivo.nome_arquivo)
            caminho_pasta = self.__filemanager.caminho(arquivo.nome_extracao, data)

            caminho_arquivo = os.path.join(caminho_pasta, arquivo.nome_extracao)

            arq = None

            extraiu = False

            if os.path.isfile(caminho_arquivo):
                arq = open(caminho_arquivo, encoding='utf-8', mode='r', errors="ignore")

            if arq:
                extraiu = self.inicia_extrator(arq, arquivo,tag)
            else:
                ConfigManager().escreve_log("Arquivo {} faltando!".format(caminho_arquivo), self.__robo, self.__erro)

            if extraiu:
                if 'producao' in default_schema:
                    self.__filemanager.preenche_csv_arquivo_extraido(arquivo.nome_extracao)
                self.set_arquivo_extraido(arquivo, extrator,tag)

    # ATENÇÃO! ESTE MÉTODO NÃO LEVA EM CONTA O STATUS EXTRAÍDO!
    # ELE EXTRAI UM DIÁRIO MESMO QUE JÁ TENHA SIDO EXTRAÍDO ANTES!
    def extrai_diversos_independente_de_status(self, padrao=None,tag='FALENCIAS'):
        arquivo_service = ArquivoService()
        extrator_service = ExtratorService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)
        arquivos_totais = arquivo_service.dao.get_arquivos_por_diario(self.__extrator.nome_diario)
        self._realiza_extracao_de_arquivos(arquivos_totais, extrator, padrao,tag)

    def extrai_diversos_que_nao_foram_extraidos_a_partir_da_data(self, data,padrao=None,tag=None,fatia=1,rank=0):
        arquivo_service = ArquivoService()
        extrator_service = ExtratorService()
        extrator = extrator_service.preenche_extrator(self.__extrator.__name__)
        arquivos_totais = arquivo_service.dao.get_arquivos_nao_extraido_a_partir_da_data(extrator,self.__extrator.nome_diario,data,fatia=fatia,rank=rank)
        self._realiza_extracao_de_arquivos(arquivos_totais, extrator, padrao,tag)
