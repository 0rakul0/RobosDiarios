from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.ClasseCredor import ClasseCredor
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais


class ClasseCredorDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ClasseCredorDao, self).__init__(ClasseCredor)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(nome))).upper()
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(nome))).upper()
            return self._classe.select().where(ClasseCredor._nome.contains(nome))
        except self._classe.DoesNotExist as e:
            return None