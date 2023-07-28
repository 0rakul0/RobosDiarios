
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Situacao import Situacao
from util.StringUtil import remove_varios_espacos, remove_acentos


class SituacaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(SituacaoDao, self).__init__(Situacao)

    def get_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None