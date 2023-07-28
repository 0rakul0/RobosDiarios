# -*- coding: utf-8 -*-
import hashlib

from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Movimento import Movimento

class Sentenca(BaseClass):
    __tablename__ = "sentenca"
    id = PrimaryKeyField(null=False)
    data = DateTimeField()
    _descricao = TextField(db_column="descricao") #nas habilitações pode ser a classe do crédito.
    processo = ForeignKeyField(Processo,null=True,related_name="sentencas")
    movimento = ForeignKeyField(Movimento, null=True)
    _situacao = TextField(db_column="situacao") #DEFERIDA, INDEFERIDA.....
    valor = DecimalField()
    tipo_moeda = TextField()
    _hash_descricao = TextField(db_column="hash_descricao")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Sentenca, self).__init__(*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um Sentenca sem processo!")
            return False
        return True

    @property
    def descricao(self):
        self._descricao = remove_varios_espacos(remove_acentos(self._descricao.upper()))
        return self._descricao

    @descricao.setter
    def descricao(self, value):
        if value:
            self._descricao = remove_varios_espacos(remove_acentos(value.upper()))
            self._hash_descricao = hashlib.md5(self._descricao.encode('utf-8')).hexdigest()

    @property
    def situacao(self):
        self._situacao = remove_varios_espacos(remove_acentos(self._situacao.upper()))
        return self._situacao

    @situacao.setter
    def situacao(self, value):
        if value:
            self._situacao= remove_varios_espacos(remove_acentos(value.upper()))
