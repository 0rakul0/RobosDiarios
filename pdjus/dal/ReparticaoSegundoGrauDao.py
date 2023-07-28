from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.ReparticaoSegundoGrau import ReparticaoSegundoGrau
from util.StringUtil import remove_acentos,remove_varios_espacos


class ReparticaoSegundoGrauDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ReparticaoSegundoGrauDao, self).__init__(ReparticaoSegundoGrau)

    def get_por_nome_e_tribunal(self,nome,tribunal):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.get(self._classe._nome == nome, self._classe.tribunal == tribunal)
        except self._classe.DoesNotExist as e:
            return None

