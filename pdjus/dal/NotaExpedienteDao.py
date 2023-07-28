__author__ = 'B249025230'

from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.NotaExpediente import NotaExpediente

class NotaExpedienteDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(NotaExpedienteDao, self).__init__(NotaExpediente)

    def get_por_movimento_cod_ano_data(self,movimento,cod_ano,data):
        try:
            return self._classe.get((self._classe.movimento == movimento), (self._classe.cod_ano == cod_ano), (self._classe.data == data))
        except self._classe.DoesNotExist as e:
            return None
