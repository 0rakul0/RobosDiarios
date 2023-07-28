# -*- coding: utf-8 -*-
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Caderno import Caderno
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.DadoExtraido import DadoExtraido

class HistoricoDado(BaseClass):
    id = PrimaryKeyField(null=False)

    dado_extraido = ForeignKeyField(DadoExtraido, null=True, related_name="historicos")

    caderno = ForeignKeyField(Caderno,null=True)

    data_extracao = DateTimeField()

    marcador = CharField()

    local_extracao = CharField()


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(HistoricoDado, self).__init__(["dado_extraido","caderno","data_extracao","marcador"],*args, **kwargs)

    def is_valido(self):
        if not self.dado_extraido:
            print("Não pode existir um HistoricoDado sem dado extraido!")
            return False
        if not self.marcador:
            print("Não pode existir um HistoricoDado sem Tag/marcador!")
            return False
        return True

    class Meta:
        db_table = "historico_dado"