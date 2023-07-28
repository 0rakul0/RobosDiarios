from pdjus.modelo.Movimento import Movimento
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *

class NotaExpediente(BaseClass):
    id = PrimaryKeyField(null=False)
    cod_ano = CharField()
    data = DateTimeField()
    texto = TextField()

    movimento = ForeignKeyField(Movimento,null=True,related_name="nota_expediente")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(NotaExpediente, self).__init__(["data","texto","movimento"],*args, **kwargs)

    def is_valido(self):
        if not self.movimento:
            print("Não pode existir um NotaExpediente sem movimento!")
            return False
        return True

    class Meta:
        db_table = "nota_expediente"
