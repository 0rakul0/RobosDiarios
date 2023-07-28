
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Prova import Prova
from pdjus.modelo.Processo import Processo

class ProvaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ProvaDao, self).__init__(Prova)

    def get_por_processo(self,processo):
        try:
            return self._classe.select().where(self._classe.processo == processo)
        except self._classe.DoesNotExist as e:
            return None



    def get_por_informacoes(self, nome, descricao, processo=None):
        try:
            return self._classe.select().join(Processo).\
                where(self._classe._nome == nome, self._classe.descricao == descricao,
                      Processo.id == processo.id if processo else True)
        except self._classe.DoesNotExist as e:
            return None



    def listar_por_nome(self, nome):
        try:
            return self._classe.select().where(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_limite_por_nome(self, start, stop, nome):
        try:
            return self._classe.select().order_by(
                self._classe.id).where(self._classe._nome == nome).slice(start, stop)
        except self._classe.DoesNotExist as e:
            return None
