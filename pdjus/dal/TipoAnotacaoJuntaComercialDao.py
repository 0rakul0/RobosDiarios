from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao
from pdjus.modelo.TipoAnotacaoJuntaComercial import TipoAnotacaoJuntaComercial

class TipoAnotacaoJuntaComercialDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(TipoAnotacaoJuntaComercialDao, self).__init__(TipoAnotacaoJuntaComercial)

    def get_por_tipo_anotacao_junta_comercial(self, junta_comercial, tipo_anotacao):
        try:
            return self._classe.select().where(self._classe.junta_comercial==junta_comercial,self._classe.tipo_anotacao==tipo_anotacao).get()
        except self._classe.DoesNotExist as e:
            return None

