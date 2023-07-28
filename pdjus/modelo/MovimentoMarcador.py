from pdjus.modelo.Marcador import Marcador
from pdjus.modelo.Movimento import Movimento
from pdjus.modelo.BaseClass import *

class MovimentoMarcador (BaseClass):
    id = PrimaryKeyField(null=False)
    movimento = ForeignKeyField(Movimento, null=False, related_name='movimento_marcadores')
    marcador = ForeignKeyField(Marcador, null=False)
    #observacao = CharField(db_column="observacao")

    def is_valido(self):
        if not self.movimento:
            print("Não pode existir um movimento marcador sem movimento!")
            return False
        if not self.marcador:
            print("Não pode existir um movimento marcador sem marcador!")
            return False
        return True

    class Meta:
        db_table = "movimento_marcador"