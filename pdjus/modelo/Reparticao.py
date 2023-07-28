from pdjus.modelo.Comarca import Comarca
from pdjus.modelo.Tribunal import Tribunal
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *

class Reparticao(BaseClass):
    __tablename__ = "reparticao"
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    comarca = ForeignKeyField(Comarca,null=True, related_name="reparticoes")
    tribunal = ForeignKeyField(Tribunal, null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Reparticao, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Reparticao sem nome!")
            return False
        if not self.comarca and not self.tribunal:
            print("Não pode existir um Reparticao sem comarca e  sem tribunal!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))