from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.Enquadramento import Enquadramento
from pdjus.modelo.BaseClass import *

class EmpresaEnquadramento (BaseClass):
    id = PrimaryKeyField(null=False)
    empresa = ForeignKeyField(Empresa, null=True)
    enquadramento = ForeignKeyField(Enquadramento, null=True)

    def is_valido(self):
        if not self.empresa:
            print("Não pode existir uma Empresa Enquadramento sem Empresa!")
            return False
        if not self.enquadramento:
            print("Não pode existir uma Empresa Enquadramento sem Enquadramento!")
            return False
        return True

    class Meta:
        db_table = "empresa_enquadramento"