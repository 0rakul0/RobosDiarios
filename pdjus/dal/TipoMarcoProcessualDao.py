from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.TipoMarcoProcessual import TipoMarcoProcessual
from util.StringUtil import remove_acentos,remove_varios_espacos


class TipoMarcoProcessualDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(TipoMarcoProcessualDao, self).__init__(TipoMarcoProcessual)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None
