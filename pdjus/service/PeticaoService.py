from pdjus.conexao.Conexao import Singleton
from pdjus.dal.PeticaoDao import PeticaoDao
from pdjus.modelo.Peticao import Peticao
from pdjus.service.BaseService import BaseService


class PeticaoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(PeticaoService, self).__init__(PeticaoDao())

    def preenche_peticao(self, data, processo, texto, tipo=None):
        if processo.id is not None:
            peticao = self.dao.get_por_processo_data_descricao_tipo(processo, data, texto, tipo)
        if peticao is None:
            peticao = Peticao()
            peticao.data = data
            peticao.descricao = texto
            #peticao.tipo = tipo
            peticao.processo = processo
            self.salvar(peticao)
        return peticao