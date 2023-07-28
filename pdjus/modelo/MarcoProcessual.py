
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.Movimento import Movimento
# from pdjus.modelo.NotaExpediente import NotaExpediente
from pdjus.modelo.TipoMarcoProcessual import TipoMarcoProcessual


class MarcoProcessual(BaseClass):
    id = PrimaryKeyField(null=False)

    movimento = ForeignKeyField(Movimento,null=True, related_name="marcos_processuais")

    # nota_expediente = ForeignKeyField(NotaExpediente,null=True,related_name="marcos_processuais")

    tipo_marco_processual = ForeignKeyField(TipoMarcoProcessual,null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(MarcoProcessual, self).__init__(["movimento","tipo_marco_processual"],*args, **kwargs)

    def is_valido(self):
        if not self.movimento:
            print("Não pode existir um MarcoProcessual sem movimento!")
            return False
        return True

    class Meta:
        db_table = "marco_processual"