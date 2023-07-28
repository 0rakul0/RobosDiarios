from pdjus.modelo.Arquivo import Arquivo
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Extrator import Extrator


class StatusExtraido(BaseClass):
    id = PrimaryKeyField(null=False)

    arquivo = ForeignKeyField(Arquivo,null=True,related_name="status_extraido")

    extrator = ForeignKeyField(Extrator,null=True)

    data = DateTimeField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(StatusExtraido, self).__init__(*args, **kwargs)

    def is_valido(self):
        if not self.arquivo:
            print("Não pode existir um StatusExtraido sem arquivo!")
            return False
        if not self.extrator:
            print("Não pode existir um StatusExtraido sem extrator!")
            return False
        return True

    class Meta:
        db_table = "status_extraido"