from pdjus.modelo.Estado import Estado
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *


TribunalEstadoThroughDeferred = DeferredThroughModel()
class Tribunal(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    estado = ForeignKeyField(Estado, null=True)
    estados = ManyToMany(Estado,through_model=TribunalEstadoThroughDeferred)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Tribunal, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Tribunal sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

class TribunalEstado(BaseClass):
     tribunal = ForeignKeyField(Tribunal,null=True)
     estado = ForeignKeyField(Estado,null=True)
     class Meta:
         primary_key = CompositeKey('tribunal', 'estado')
         db_table = "tribunal_estado"

TribunalEstadoThroughDeferred.set_model(TribunalEstado)