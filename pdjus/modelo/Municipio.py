__author__ = 'B249025230'

from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Estado import Estado

class Municipio(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    numero_ibge = IntegerField()
    #id_muni_prev = IntegerField()
    estado = ForeignKeyField(Estado)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Municipio, self).__init__(["nome", "numero_ibge","estado"],*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Municipio sem nome!")
            return False
        if not self.estado:
            print("Não pode existir um Municipio sem estado!")
            return False
        return True


    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

