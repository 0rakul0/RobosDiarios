# -*- coding: utf-8 -*-
from datetime import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.SentencaDao import SentencaDao
from pdjus.modelo.Sentenca import Sentenca
from pdjus.service.BaseService import BaseService


class SentencaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(SentencaService, self).__init__(SentencaDao())


    def preenche_sentenca(self, processo , data,descricao=None,movimento = None, situacao = None,tipo_moeda=None,valor=None):
        sentenca = None
        if type(data) is str:
            data = datetime.strptime(data, "%d/%m/%Y")
        if movimento:
            sentenca = self.dao.get_por_movimento_situacao_descricao_valor_tipo_moeda(movimento, situacao=situacao,
                                                                                     descricao=descricao,
                                                                                     tipo_moeda=tipo_moeda, valor=valor)
        if not sentenca:
            sentenca = self.dao.get_por_processo_data_descricao(processo, descricao=descricao,data=data)
        if not sentenca:
            sentenca = Sentenca()
            if movimento:
                sentenca.movimento = movimento
                sentenca.processo = movimento.processo
            elif processo:
                sentenca.processo = processo
            if situacao:
                sentenca.situacao = situacao
            sentenca.data = data
            sentenca.descricao = descricao
            sentenca.tipo_moeda = tipo_moeda
            sentenca.valor = valor
            self.salvar(sentenca)
        return sentenca