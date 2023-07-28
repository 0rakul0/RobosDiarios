
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Tribunal import Tribunal

class ReparticaoSegundoGrau(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    tribunal = ForeignKeyField(Tribunal,null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ReparticaoSegundoGrau, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um ReparticaoSegundoGrau sem nome!")
            return False
        if not self.tribunal:
            print("Não pode existir um ReparticaoSegundoGrau sem tribunal!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    class Meta:
        db_table = "reparticao_segundo_grau"