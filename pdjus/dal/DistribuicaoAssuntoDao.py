from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao

from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.DistribuicaoAssunto import DistribuicaoAssunto

from util.StringUtil import remove_acentos,remove_varios_espacos

class DistribuicaoAssuntoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(DistribuicaoAssuntoDao, self).__init__(DistribuicaoAssunto)

    def get_por_distribuicao_assunto(self, distribuicao, assunto):
        try:
            return self._classe.select().where(self._classe.distribuicao==distribuicao,self._classe.assunto==assunto).get()
        except self._classe.DoesNotExist as e:
            return None
