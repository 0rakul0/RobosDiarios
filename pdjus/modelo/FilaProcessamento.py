# -*- coding: utf-8 -*-
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Servidor import Servidor

class FilaProcessamento(BaseClass):

    id = PrimaryKeyField(null=False)
    tribunal_id = IntegerField(db_column="tribunal_id")
    servidor = ForeignKeyField(Servidor, null=True)
    processado = BooleanField(db_column="processado")
    secao = CharField(db_column="secao")

    def is_valido(self):
        return True

    class Meta:
        db_table = "fila_processamento"