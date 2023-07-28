# -*- coding: utf-8 -*-

from util.StringUtil import remove_varios_espacos, remove_acentos
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.TipoJunta import TipoJunta

class TipoJuntaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(TipoJuntaDao, self).__init__(TipoJunta)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None