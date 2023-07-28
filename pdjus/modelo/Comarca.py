
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Tribunal import Tribunal
from pdjus.modelo.Estado import Estado

class Comarca(BaseClass):
    id = PrimaryKeyField(null=False)
    codigo_comarca = CharField()
    _nome = CharField(db_column='nome')
    tribunal = ForeignKeyField(Tribunal,null=True, related_name="comarcas")
    #estado = ForeignKeyField(Estado, null=True)

    nome_formatado = CharField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)
    
    def init_on_load(self,*args, **kwargs):
        super(Comarca, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Comarca sem nome!")
            return False

        return True

    @property
    def nome(self):
        if self._nome:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        if value:
            self._nome = remove_varios_espacos(remove_acentos(value.upper()))
