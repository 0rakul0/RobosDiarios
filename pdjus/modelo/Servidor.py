# -*- coding: utf-8 -*-
from pdjus.modelo.BaseClass import *

class Servidor(BaseClass):

    id = PrimaryKeyField(null=False)
    nome = CharField(db_column="nome")
    cpf = CharField(db_column="cpf")

    def is_valido(self):
        return True