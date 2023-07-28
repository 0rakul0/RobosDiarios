from util.StringUtil import remove_varios_espacos, remove_acentos,remove_links
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Marcador import Marcador

class MarcadorDao(GenericoDao,metaclass=Singleton):

    def __init__(self):
        super(MarcadorDao, self).__init__(Marcador)


    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            obj = self._classe.get(self._classe._nome == nome)
            return obj
        except self._classe.DoesNotExist as e:
            return None