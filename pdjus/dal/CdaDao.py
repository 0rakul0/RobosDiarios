from pdjus.dal.GenericoDao import *
from pdjus.modelo.Cda import Cda
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links

class CdaDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(CdaDao, self).__init__(Cda)

    def get_por_processo_texto(self, processo, texto):
        try:
            return self._classe.select().join(Processo).where((self._classe._texto == texto), self._classe.processo == processo).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_texto(self, texto):
        try:
            if texto:
                texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))

                return self._classe.get(self._classe._texto.contains(texto))
        except self._classe.DoesNotExist as e:
            return None