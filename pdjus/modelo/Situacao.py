
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos

class Situacao(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Situacao, self).__init__(*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Situacao sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
