
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
# from pdjus.modelo.Processo import Processo
from pdjus.modelo.MarcoProcessual import MarcoProcessual
from pdjus.modelo.DispositivoLegal import DispositivoLegal

class MarcoProcessualDispositivoLegal(BaseClass):
    id = PrimaryKeyField(null=False)

    marco_processual = ForeignKeyField(MarcoProcessual,null=True,related_name="marcos_processuais_dispositivos_legais")

    dispositivo_legal = ForeignKeyField(DispositivoLegal,null=True,related_name="marcos_processuais_dispositivos_legais")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(MarcoProcessualDispositivoLegal, self).__init__(["marco_processual","dispositivo_legal"],*args, **kwargs)

    def is_valido(self):
        if not self.marco_processual:
            print("Não pode existir um MarcoProcessualDispositivoLegal sem marco processual!")
            return False
        return True

    class Meta:
        db_table = "marco_processual_dispositivo_legal"
