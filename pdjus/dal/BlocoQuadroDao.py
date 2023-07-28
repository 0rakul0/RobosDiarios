from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.modelo.Processo import Processo
from pdjus.modelo.QuadroCredor import QuadroCredor

class BlocoQuadroDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(BlocoQuadroDao, self).__init__(BlocoQuadro)

    def get_por_texto(self,texto):
        try:
            # texto =remove_varios_espacos(remove_acentos(remove_caracteres_especiais(texto.strip().upper())))
            return self._classe.select().where(self._classe._texto == texto).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_movimento(self,movimento):
        try:
            # texto =remove_varios_espacos(remove_acentos(remove_caracteres_especiais(texto.strip().upper())))
            return self._classe.select().where(self._classe.movimento == movimento).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo(self,processo):
        try:
            return self._classe.select(self._classe).distinct().join(QuadroCredor).join(Processo).where(Processo.id == processo.id)
        except self._classe.DoesNotExist as e:
            return None