# -*- coding: utf-8 -*-

from util.StringUtil import remove_varios_espacos, remove_acentos
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.TipoParte import TipoParte

class TipoParteDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(TipoParteDao, self).__init__(TipoParte)

    def get_por_nome(self,nome,cache=True):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            if cache:
                    obj = self.get_cached_object(nome)
                    if not obj:
                        obj = self._classe.get(self._classe._nome == nome)
                        if obj:
                            self.add_to_cache(obj)
                    return obj
            else:
                return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None