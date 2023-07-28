from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from pdjus.modelo.JuntaComercial import JuntaComercial

class ProcessoJuntaComercial (BaseClass):
    id = PrimaryKeyField(null=False)
    processo_id = IntegerField(null=False, db_column="processo_id")
    junta_comercial_id = IntegerField(null=False, db_column="junta_comercial_id")

    def is_valido(self):
        if not self.processo_id:
            print("Não pode existir um ID da Junta Comercial sem um ID do Processo!")
            return False
        if not self.junta_comercial_id:
            print("Não pode existir um ID do Processo sem um ID da Junta Comercial!")
            return False
        return True

    class Meta:
        db_table = "processo_junta_comercial"
