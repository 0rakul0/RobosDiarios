
from pdjus.modelo.PessoaFisica import PessoaFisica
from pdjus.dal.GenericoDao import *

class PessoaFisicaDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(PessoaFisicaDao, self).__init__(PessoaFisica)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def list_por_nome_like(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome.contains('{}'.format(nome)))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_cpf(self,cpf):
        try:
            cpf = remove_varios_espacos(remove_acentos(cpf))
            return self._classe.get(self._classe._cpf == cpf)
        except self._classe.DoesNotExist as e:
            return None

    def listar_nao_processados(self, fatia=1, rank=0):
        try:
            return self.listar(fatia=fatia,rank=rank,).select().where(self._classe.processado == False)
        except self._classe.DoesNotExist as e:
            return None