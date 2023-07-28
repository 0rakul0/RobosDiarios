from pdjus.conexao.Conexao import Singleton
from pdjus.dal.JuizDao import JuizDao
from pdjus.modelo.Juiz import Juiz
from pdjus.service.BaseService import BaseService


class JuizService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(JuizService, self).__init__(JuizDao())

    def preenche_juiz(self,nome):
        juiz = self.dao.get_por_nome(nome)
        if not juiz:
            juiz = Juiz()
            juiz.nome = nome
            self.salvar(juiz)
        return juiz