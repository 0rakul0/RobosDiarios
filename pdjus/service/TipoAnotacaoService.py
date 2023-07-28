from pdjus.conexao.Conexao import Singleton
from pdjus.dal.TipoAnotacaoDao import TipoAnotacaoDao
from pdjus.modelo.TipoAnotacao import TipoAnotacao
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos,remove_caracteres_especiais

class TipoAnotacaoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(TipoAnotacaoService, self).__init__(TipoAnotacaoDao())

    def preenche_tipo_anotacao(self, nome):
        tipo_anotacao = None
        nome = nome.upper()
        if nome != '':
            tipo_anotacao = self.dao.get_por_nome(nome)
            if not tipo_anotacao:
                tipo_anotacao = TipoAnotacao()
                tipo_anotacao.nome = nome
                self.salvar(tipo_anotacao)
        return tipo_anotacao