__author__ = 'B247830755'

from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Incidente import Incidente
from util.StringUtil import remove_acentos, remove_varios_espacos



class IncidenteDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(IncidenteDao, self).__init__(Incidente)

    def get_por_processo_data_descricao(self, processo, data, descricao):
        try:
            descricao = remove_acentos(remove_varios_espacos(descricao.upper()))
            return self._classe.get((self._classe.processo == processo),
                                                            (self._classe.data == data),
                                                            (self._classe._descricao == descricao))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo(self, processo):
        try:
            return self._classe.get((self._classe.processo == processo))
        except self._classe.DoesNotExist as e:
            return None
