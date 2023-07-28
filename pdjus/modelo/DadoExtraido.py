# -*- coding: utf-8 -*-


from pdjus.modelo.BaseClass import *

class DadoExtraido(BaseClass):
    id = PrimaryKeyField(null=False)
    data_entrada = DateTimeField()



    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(DadoExtraido, self).__init__(*args, **kwargs)

    def is_valido(self):
        if not self.data_entrada:
            print("Não pode existir um DadoExtraido sem data_entrada!")
            return False
        return True

    class Meta:
        db_table = "dado_extraido"
