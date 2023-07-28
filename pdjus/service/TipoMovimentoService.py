from pdjus.conexao.Conexao import Singleton
from pdjus.dal.TipoMovimentoDao import TipoMovimentoDao
from pdjus.modelo.TipoMovimento import TipoMovimento
from pdjus.service.BaseService import BaseService


class TipoMovimentoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(TipoMovimentoService, self).__init__(TipoMovimentoDao())

    def preenche_tipo_movimento(self, nome, is_inteiro_teor=False):
        tipoMovimento = self.dao.get_por_nome(nome)
        if not tipoMovimento:
            tipoMovimento = TipoMovimento()
            tipoMovimento.nome = nome
            tipoMovimento.is_inteiro_teor = is_inteiro_teor
            self.salvar(tipoMovimento)

        return tipoMovimento