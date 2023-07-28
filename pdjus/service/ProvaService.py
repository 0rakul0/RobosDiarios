from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ProvaDao import ProvaDao
from pdjus.modelo.Prova import Prova
from pdjus.service.BaseService import BaseService


class ProvaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ProvaService, self).__init__(ProvaDao().get_por_informacoes())

    def preenche_prova(self,nome,descricao,processo=None):
        prova = self.dao.get_por_informacoes(nome, descricao, processo)

        if prova is None:
            prova = Prova()

        prova.nome = nome
        prova.descricao = descricao
        prova.processo = processo

        self.salvar(prova)

        return prova
