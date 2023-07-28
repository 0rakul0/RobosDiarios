__author__ = 'B247830755'

from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Processo import Processo


class Audiencia(BaseClass):
    id = PrimaryKeyField(null=False)
    _descricao = CharField(db_column="descricao")
    data = DateTimeField()
    _status = CharField(db_column="status")
    _quantidade_pessoas =  CharField(db_column="quantidade_pessoas")

    processo = ForeignKeyField(Processo,null=True, related_name="audiencias")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Audiencia, self).__init__(["descricao","data","processo"],*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um audiencia sem processo!")
            return False

        return True


    @property
    def descricao(self):
        if self._descricao:
            self._descricao = remove_varios_espacos(remove_acentos(self._descricao.upper()))
        return self._descricao

    @descricao.setter
    def descricao(self, value):
        if value:
            self._descricao = remove_varios_espacos(remove_acentos(value.upper()))

    @property
    def status(self):
        if self._status:
            self._status = remove_varios_espacos(remove_acentos(self._status.upper()))
        return self._status

    @status.setter
    def status(self, value):
        if value:
            self._status = remove_varios_espacos(remove_acentos(value.upper()))

    @property
    def quantidade_pessoas(self):
        if self._quantidade_pessoas:
            self._quantidade_pessoas = remove_varios_espacos(remove_acentos(self._quantidade_pessoas.upper()))
        return self._quantidade_pessoas

    @quantidade_pessoas.setter
    def quantidade_pessoas(self, value):
        if value:
            self._quantidade_pessoas = remove_varios_espacos(remove_acentos(value.upper()))

