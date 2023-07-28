# -*- coding: utf-8 -*-
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links


class Diario(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome =  CharField(db_column="nome")
    data = DateTimeField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Diario, self).__init__(["nome","data"],*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Diario sem nome!")
            return False
        # if not self.data:
        #     print("Não pode existir um Diario sem data!")
        #     return False
        return True

    @property
    def nome(self):
        if self._nome is not None:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
            return self._nome
        else:
            return None

    @nome.setter
    def nome(self, value):
        if value is not None:
            self._nome = remove_varios_espacos(remove_acentos(value.upper()))