from pdjus.conexao.Conexao import Singleton
from pdjus.dal.SituacaoDao import SituacaoDao
from pdjus.modelo.Situacao import Situacao
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_tracos_pontos_barras_espacos, remove_acentos


class SituacaoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(SituacaoService, self).__init__(SituacaoDao())

    def preenche_situacao(self,nome_situacao):
        nome_situacao = remove_acentos(remove_tracos_pontos_barras_espacos(nome_situacao))
        situacao = self.dao.get_por_nome(nome_situacao.upper())

        if not situacao:
            situacao = Situacao()
            situacao.nome = nome_situacao.upper()
            self.salvar(situacao)
        return situacao