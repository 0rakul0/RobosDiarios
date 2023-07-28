from pdjus.conexao.Conexao import Singleton
from pdjus.dal.PessoaFisicaDao import PessoaFisicaDao
from pdjus.modelo.PessoaFisica import PessoaFisica
from pdjus.service.BaseService import BaseService


class PessoaFisicaService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(PessoaFisicaService, self).__init__(PessoaFisicaDao())

    def preenche_pessoa(self,nome,cpf=None):
        pessoa = None
        if cpf:
            pessoa = self.dao.get_por_cpf(cpf)
        if not pessoa:
            pessoa = PessoaFisica()
            pessoa.nome = nome
            pessoa.cpf = cpf

            self.salvar(pessoa)

        return pessoa