import datetime

from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.BaseClass import *



class DistribuicaoAssunto (BaseClass):
    id = PrimaryKeyField(null=False)
    distribuicao = ForeignKeyField(Distribuicao, null=True)
    assunto = ForeignKeyField(Assunto, null=True)
    _data = DateTimeField(db_column="data")

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        if type(value) is datetime.datetime or type(value) is datetime.date:
            self._data = value
        else:
            self._data = datetime.datetime.strptime(value, '%Y/%m/%d')

    def is_valido(self):
        if not self.distribuicao:
            print("Não pode existir um Distribuicao Assunto sem distribuiçao!")
            return False
        if not self.assunto:
            print("Não pode existir um Distribuicao Assunto sem Assunto!")
            return False
        return True

    class Meta:
        db_table = "distribuicao_assunto"
