__author__ = 'B247830755'

from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Processo import Processo


class Peticao(BaseClass):
    id = PrimaryKeyField(null=False)
    _descricao =  CharField(db_column="descricao")
    #_tipo = CharField(db_column="tipo")
    data = DateTimeField()

    processo = ForeignKeyField(Processo,null=True,related_name="peticoes")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Peticao, self).__init__(["descricao","data","processo"],*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um Peticao sem processo!")
            return False
        return True

    @property
    def descricao(self):
        self._descricao = remove_varios_espacos(remove_acentos(self._descricao.upper()))
        return self._descricao

    @descricao.setter
    def descricao(self, value):
        self._descricao = remove_varios_espacos(remove_acentos(value.upper()))

    # @property
    # def tipo(self):
    #     self._tipo = remove_varios_espacos(remove_acentos(self._tipo.upper()))
    #     return self._tipo
    #
    # @tipo.setter
    # def tipo(self, value):
    #     self._tipo = remove_varios_espacos(remove_acentos(value.upper()))