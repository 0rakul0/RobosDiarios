# -*- coding: utf-8 -*-
import re
from datetime import datetime
from extrator.ProcessaExtrator import ProcessaExtrator
from pdjus.dal.EstadoDao import EstadoDao
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from pdjus.service.DiarioService import DiarioService
from pdjus.service.DistribuicaoService import DistribuicaoService
from pdjus.service.EstadoService import EstadoService
from util.DateUtil import parse_mes_para_num


class ExtratorCPCSTJ:
    nome_diario = "STJ"

    def __init__(self, nome, arquivo):
        self._arquivo = arquivo
        self.__nome = nome
        self.__diario = self.get_diario()

    def is_edital(self):
        pass

    def extrai(self,tag=None):
        data = None
        linha_anterior = ""
        lista = self.criar_lista_de_linhas()
        for linha in lista:
            linha_nova = linha_anterior + " " + linha
            if not data:
                data = self.pega_data_distribuicao(linha_nova)
            if data:
                self.pega_distribuicao(linha,data)
            if data and self.terminou_ata_de_ditribuicoes(linha_nova):
                data = None
            linha_anterior = linha


    def get_diario(self):
        nome_diario = "STJ"
        data = self.pega_data_caderno_nome_arquivo()
        data = datetime.strptime(data, "%Y_%m_%d")

        diario_service = DiarioService()
        diario = diario_service.preenche_diario(nome_diario,data)

        return diario



    def pega_data_distribuicao(self,linha):
        result = re.search("Registro *e *Distribui.* .*dia *(\d{2}).*(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro).*(\d{4})",linha,flags = re.IGNORECASE)

        if result:
            day = int(result.group(1))
            month = parse_mes_para_num(result.group(2))
            year = int(result.group(3))
            if day and month and year:
                data = datetime(year,month,day)
                return data

        return None

    # TODO: O extrator do CPC tenta usar propriedades que não existem mais em Distribuicao
    def pega_distribuicao(self,linha,data):
        result = re.search("(.*)Nº *\d* *\- *(\w{2}) *\((\d{4}\/\d*\-\d)\)",linha,flags = re.IGNORECASE)

        if result:
            distribuicao = Distribuicao()
            distribuicao.numero_distribuicao = result.group(3)
            estado_service = EstadoService()
            estado = estado_service.preenche_estado(result.group(2))
            if estado:
                distribuicao.estado = estado

            classe_processual_service = ClasseProcessualService()
            classe_processual = classe_processual_service.preenche_classe_processual(result.group(1))

            distribuicao.classe_processual = classe_processual

            distribuicao.data_distribuicao = data.date()

            distribuicao.diario = self.__diario

            distribuicao_service = DistribuicaoService()

            distribuicao_service.salvar(distribuicao)





    def criar_lista_de_linhas(self):
        lista = []
        linha_atual = ''
        linha_anterior = ''
        for line in self._arquivo:
            linha_atual = line.strip('\n').strip('\f')
            if linha_atual == '':
                continue
            else:
                self.concatena_linhas(linha_atual,lista)

        return lista

    def concatena_linhas(self, linha_atual, lista):
        ultima_posicao = -1
        if len(lista) > 0 and len(lista[ultima_posicao]) >= 2 and lista[ultima_posicao][-1] == '-' and lista[ultima_posicao][-2] != ' ':
            lista[ultima_posicao] = lista[ultima_posicao][:-1]
            lista[ultima_posicao] = lista[ultima_posicao] + linha_atual
        else:
            lista.append(linha_atual)

        return lista

    def ignora_numero_de_pagina(self, linha_anterior, linha_atual):
        if linha_atual.isdigit():
            ignora_linha= True
            linha_atual = linha_anterior
        else:
            ignora_linha = False
        return linha_atual, ignora_linha

    def pega_data_caderno_nome_arquivo(self):
        data = re.search('.*(\d{4}_\d{2}_\d{2})',self._arquivo.name)
        return data.group(1) if (data is not None) else data

    def terminou_ata_de_ditribuicoes(self, linha):
        result = re.search("Distribu.dos *Redistr.bu.dos",linha,flags = re.IGNORECASE)
        return True if result else False

if __name__ == '__main__':
    p = ProcessaExtrator("STJ", "txt", ExtratorCPCSTJ)
    p.extrai_diversos()