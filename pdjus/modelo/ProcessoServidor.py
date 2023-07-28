# -*- coding: utf-8 -*-
from pdjus.modelo.BaseClass import *

class ProcessoServidor(BaseClass):
    id = PrimaryKeyField(null=False)
    numero = CharField(db_column="numero")
    servidor_id = IntegerField(db_column="servidor_id")
    tribunal_id = IntegerField(db_column="tribunal_id")

    def is_valido(self):
        return True

    class Meta:
        db_table = "processo_servidor"