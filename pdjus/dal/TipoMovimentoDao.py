from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.TipoMovimento import TipoMovimento
from util.StringUtil import remove_acentos,remove_varios_espacos


class TipoMovimentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(TipoMovimentoDao, self).__init__(TipoMovimento)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.select().where(self._classe._nome == nome).get()
        except self._classe.DoesNotExist as e:
            return None