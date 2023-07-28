from util.StringUtil import remove_varios_espacos, remove_acentos,remove_links
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Cnae import Cnae

class CnaeDao(GenericoDao,metaclass=Singleton):

    def __init__(self):
        super(CnaeDao, self).__init__(Cnae)


    def get_por_numero(self,numero):
        try:
            numero = remove_varios_espacos(remove_acentos(numero)).upper()
            obj = self._classe.get(self._classe._numero == numero)
            return obj
        except self._classe.DoesNotExist as e:
            return None