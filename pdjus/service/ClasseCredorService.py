from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ClasseCredorDao import ClasseCredorDao
from pdjus.modelo.ClasseCredor import ClasseCredor
from pdjus.service.BaseService import BaseService


class ClasseCredorService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ClasseCredorService, self).__init__(ClasseCredorDao())

    def preenche_classe_credor(self, classe):
        classe_credor = self.dao.get_por_nome(classe)

        if classe_credor is None:
            classe_credor = ClasseCredor()
            classe_credor.nome = classe
            self.salvar(classe_credor, commit=False)

        return classe_credor