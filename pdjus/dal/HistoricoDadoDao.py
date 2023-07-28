# -*- coding: utf-8 -*-


from random import randint

from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.modelo.DadoExtraido import DadoExtraido


class HistoricoDadoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(HistoricoDadoDao, self).__init__(HistoricoDado)


    def listar_processos(self, marcador):
        try:
            return self._classe.select().join(self._classe.dado_extraido).\
                join(DadoExtraido.processos).where(self._classe.marcador ==
                                                    self._normalizar_marcador(marcador))
        except self._classe.DoesNotExist as e:
            return None

    def listar_publicacoes(self, marcador):
        try:
            return self._classe.select().join(self._classe.dado_extraido).\
                join(DadoExtraido.publicacoes).where(self._classe.marcador ==
                                                      self._normalizar_marcador(marcador))
        except self._classe.DoesNotExist as e:
            return None

    def listar_distribuicoes(self, marcador):
        try:
            return self._classe.select().join(self._classe.dado_extraido).\
                join(DadoExtraido.distribuicoes).where(self._classe.marcador ==
                                                        self._normalizar_marcador(marcador))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_marcador(self, marcador):
        try:
            return self._classe.select().where(self._classe.marcador == marcador.upper())
        except self._classe.DoesNotExist:
            return None






