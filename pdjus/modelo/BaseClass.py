from _decimal import InvalidOperation
from collections import defaultdict

from pdjus.conexao.Conexao import *
from abc import *

__author__ = 'B120558711'


class ObjetoValidado:
    def is_valido(self):
        pass


class BaseClass(Model,ObjetoValidado):
    subclasses = []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)


    atributte_cache = None

    def get_key_cache(self):
        if self.atributte_cache:
            key = ""
            for atributte_str in self.atributte_cache:
                atributte = getattr(self,atributte_str)
                if atributte:
                    key += str(atributte)
            return key
        return self.__str__()

    def is_valido(self):
        raise InvalidOperation("IMPLEMENTAR METODO!")

    class Meta:
        schema = default_schema
        database = db

    def __init__(self,atributtes=None, *args, **kwargs):
        if not type(atributtes) is list:
            self.atributte_cache = [atributtes]
        else:
            self.atributte_cache = atributtes
        super(BaseClass, self).__init__(atributtes, *args, **kwargs)

