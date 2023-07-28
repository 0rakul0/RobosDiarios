from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ReparticaoDao import ReparticaoDao
from pdjus.modelo.Reparticao import Reparticao
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos


class ReparticaoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ReparticaoService, self).__init__(ReparticaoDao())

    def preenche_reparticao(self,nome_reparticao, comarca=None,tribunal=None):
        nome_reparticao = remove_acentos(remove_varios_espacos(nome_reparticao.strip().upper()))
        reparticao = self.dao.get_por_nome_e_comarca(nome_reparticao, comarca)
        if not reparticao:
            reparticao = self.dao.get_por_nome_e_tribunal(nome_reparticao, tribunal)
        if not reparticao:
            reparticao = Reparticao()
            reparticao.nome = nome_reparticao
            reparticao.comarca = comarca
            reparticao.tribunal = tribunal
            self.salvar(reparticao)
        return reparticao