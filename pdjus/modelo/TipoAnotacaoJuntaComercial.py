from pdjus.modelo.TipoAnotacao import TipoAnotacao
from pdjus.modelo.JuntaComercial import JuntaComercial
from pdjus.modelo.BaseClass import *

class TipoAnotacaoJuntaComercial (BaseClass):
    id = PrimaryKeyField(null=False)
    tipo_anotacao = ForeignKeyField(TipoAnotacao, null=True)
    junta_comercial = ForeignKeyField(JuntaComercial, null=True)
    observacao = CharField(db_column="observacao")

    def is_valido(self):
        if not self.tipo_anotacao:
            print("Não pode existir um tipo anotacao junta comercial sem tipo anotacao!")
            return False
        if not self.junta_comercial:
            print("Não pode existir um tipo anotacao junta comercial sem junta comercial!")
            return False
        return True

    class Meta:
        db_table = "tipo_anotacao_junta_comercial"