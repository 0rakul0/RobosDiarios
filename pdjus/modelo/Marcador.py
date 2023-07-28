from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos,remove_links


class Marcador(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column="nome")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Marcador, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self._nome:
            print("Não pode existir um marcador sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_links(remove_varios_espacos(remove_acentos(self._nome.upper())))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_links(remove_varios_espacos(remove_acentos(value.upper())))
