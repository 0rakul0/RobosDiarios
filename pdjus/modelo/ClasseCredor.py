
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais
from pdjus.modelo.BaseClass import *

class ClasseCredor(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ClasseCredor, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Classe Credor sem nome!")
            return False

        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(self._nome.strip().upper())))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(value.strip().upper())))

    class Meta:
        db_table = "classe_credor"