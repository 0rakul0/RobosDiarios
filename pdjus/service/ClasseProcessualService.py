from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ClasseProcessualDao import ClasseProcessualDao
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos


class ClasseProcessualService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ClasseProcessualService, self).__init__(ClasseProcessualDao())

    def preenche_classe_processual(self,classe,codigo_classe=None):
        if not classe:
            return None
        classe = remove_varios_espacos(remove_acentos(classe.strip().upper()))
        classe_processual = self.dao.get_por_nome(classe,cache=True)

        if not classe_processual:
            classe_processual = ClasseProcessual()
            classe_processual.nome = classe
            classe_processual.codigo_classe_processual = codigo_classe
            self.salvar(classe_processual)
        return classe_processual