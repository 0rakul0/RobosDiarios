from datetime import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.SituacaoProcessoDao import SituacaoProcessoDao
from pdjus.modelo.Situacao import Situacao
from pdjus.modelo.SituacaoProcesso import SituacaoProcesso
from pdjus.service.BaseService import BaseService
from pdjus.service.MovimentoService import *
from pdjus.service.SituacaoService import SituacaoService


class SituacaoProcessoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(SituacaoProcessoService, self).__init__(SituacaoProcessoDao())

    def preenche_situacao_processo(self, processo, situacao, data=datetime.now(), movimento= None):
        situacaoService = SituacaoService()
        situacao_processo = None
        if not type(situacao) is Situacao:
            situacao = situacaoService.preenche_situacao(situacao)

        if processo:
            situacao_processo = self.dao.get_por_situacao_e_processo(situacao, processo)
        if not situacao_processo:
            situacao_processo = SituacaoProcesso()
            situacao_processo.situacao = situacao
            situacao_processo.processo = processo
            situacao_processo.data = data
            self.salvar(situacao_processo,commit=False,salvar_estrangeiras=False)

            if movimento:
                movimentoService = MovimentoService()
                movimentoService.preenche_movimento(processo, texto=situacao.nome, tipoMovimento=movimento)
        return situacao_processo
