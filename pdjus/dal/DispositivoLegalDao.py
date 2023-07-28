from pdjus.dal.GenericoDao import *
from pdjus.modelo.DispositivoLegal import DispositivoLegal
from util.StringUtil import remove_acentos,remove_varios_espacos


class DispositivoLegalDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(DispositivoLegalDao, self).__init__(DispositivoLegal)

    def get_por_lei(self,lei):
        try:
            lei = remove_varios_espacos(remove_acentos(lei)).upper()
            return self._classe.get(self._classe._lei == lei)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_lei(self, lei):
        try:
            lei = remove_varios_espacos(remove_acentos(lei)).upper()
            return self._classe.select().where(DispositivoLegal._lei.contains(lei))
        except self._classe.DoesNotExist as e:
            return None