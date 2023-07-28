from pdjus.modelo.BaseClass import *
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.ObjetoSocial import ObjetoSocial

class EmpresaObjetoSocial (BaseClass):
    id = PrimaryKeyField(null=False)
    empresa = ForeignKeyField(Empresa, null=True)
    objeto_social = ForeignKeyField(ObjetoSocial, null=True)
    principal = BooleanField()
    fonte_dado = CharField(db_column="fonte_dado")


    def is_valido(self):
        if not self.empresa:
            print("Não pode existir uma Empresa Objeto Social sem Empresa!")
            return False
        if not self.objeto_social:
            print("Não pode existir uma Empresa Objeto Social sem Objeto!")
            return False
        return True

    class Meta:
        db_table = "empresa_objeto_social"

