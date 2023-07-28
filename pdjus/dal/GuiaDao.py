from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Guia import Guia
from util.StringUtil import remove_acentos,remove_varios_espacos, remove_links
from pdjus.modelo.Processo import Processo


class GuiaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(GuiaDao, self).__init__(Guia)

    def get_por_numero_guia(self,numero_guia):
        numero_guia = remove_links(remove_varios_espacos(remove_acentos(numero_guia.upper())))
        try:
            return self._classe.select().where(self._classe._numero_guia == numero_guia).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_processo(self,processo):
        try:
            return self._classe.select().join(Processo).where( Processo.id == processo.id)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo_e_numero_guia(self,processo,numero_guia):
        try:
            return self._classe.select().join(Processo).where((Processo.id == processo.id), (self._classe._numero_guia == numero_guia)).get()
        except self._classe.DoesNotExist as e:
            return None