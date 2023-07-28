from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ReparticaoSegundoGrauDao import ReparticaoSegundoGrauDao
from pdjus.modelo.ReparticaoSegundoGrau import ReparticaoSegundoGrau
from pdjus.service.BaseService import BaseService


class ReparticaoSegundoGrauService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ReparticaoSegundoGrauService, self).__init__(ReparticaoSegundoGrauDao())

    def preenche_reparticao_segundo_grau(self,nome_reparticao, tribunal=None):
        reparticao_segundo_grau = self.dao.get_por_nome_e_tribunal(nome_reparticao, tribunal)
        if not reparticao_segundo_grau:
            reparticao_segundo_grau = ReparticaoSegundoGrau()
            reparticao_segundo_grau.nome = nome_reparticao
            reparticao_segundo_grau.tribunal = tribunal
            self.salvar(reparticao_segundo_grau)
        return reparticao_segundo_grau