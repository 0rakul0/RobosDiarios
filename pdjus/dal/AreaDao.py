from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Area import Area
from util.StringUtil import remove_acentos,remove_varios_espacos


class AreaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(AreaDao, self).__init__(Area)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            return self._classe.select().where(Area._nome.contains(nome))
        except self._classe.DoesNotExist as e:
            return None