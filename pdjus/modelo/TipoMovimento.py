
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *

class TipoMovimento(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    _marcador_movimento = CharField(db_column="marcador_movimento")
    _is_inteiro_teor = BooleanField(db_column="is_inteiro_teor")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(TipoMovimento, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um TipoMovimento sem nome!")
            return False
        return True

    @property
    def nome(self):
        if self._nome and type(self._nome) is str:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    def marcador_movimento(self):
        self._marcador_movimento = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._marcador_movimento

    @nome.setter
    def nome(self, value):
        if value:
            self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    #@marcador_movimento.setter
    #def marcador_movimento(self, value):
       #self._marcador_movimento = remove_varios_espacos(remove_acentos(value.upper()))


    class Meta:
        db_table = "tipo_movimento"