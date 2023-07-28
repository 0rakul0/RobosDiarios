from pdjus.modelo.Cnae import Cnae
from pdjus.modelo.ObjetoSocial import ObjetoSocial
from pdjus.modelo.BaseClass import *

class CnaeObjetoSocial (BaseClass):
    id = PrimaryKeyField(null=False)
    objeto_social = ForeignKeyField(ObjetoSocial, null=True)
    cnae = ForeignKeyField(Cnae, null=True)
    observacao = CharField(db_column="observacao")

    def is_valido(self):
        if not self.objeto_social:
            print("Não pode existir um cnae objeto social sem um Objeto Social!")
            return False
        if not self.cnae:
            print("Não pode existir um cnae objeto social sem cnae!")
            return False
        return True

    class Meta:
        db_table = "cnae_objeto_social"