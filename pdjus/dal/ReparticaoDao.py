from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Reparticao import Reparticao
from util.StringUtil import remove_acentos,remove_varios_espacos


class ReparticaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ReparticaoDao, self).__init__(Reparticao)

    def get_por_nome_e_comarca(self,nome,comarca):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.get(self._classe._nome == nome, self._classe.comarca == comarca)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_tribunal(self,nome,tribunal):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.get(self._classe._nome == nome, self._classe.tribunal == tribunal)
        except self._classe.DoesNotExist as e:
            return None

