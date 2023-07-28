__author__ = 'B249025230'
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Arquivo import Arquivo
from pdjus.modelo.ProcTempTag import ProcTempTag
from util.StringUtil import remove_varios_espacos, remove_acentos

class ProcTemp(BaseClass):

    id = PrimaryKeyField(null=False)
    _numero =  CharField(db_column="numero")
    is_npu = BooleanField(db_column="is_npu")
    ano =  IntegerField(db_column="ano")
    processado = BooleanField(db_column="processado")
    encontrado = BooleanField(db_column="encontrado")
    versao =  IntegerField(db_column="versao")
    dado_entrada = CharField(db_column="dado_entrada")

    tag = ForeignKeyField(ProcTempTag)
    arquivo_origem = ForeignKeyField(Arquivo)


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ProcTemp, self).__init__(["numero","is_npu"],*args, **kwargs)

    def is_valido(self):
        return True

    @property
    def numero(self):
        if self._numero:
            self._numero = remove_varios_espacos(remove_acentos(self._numero.replace(
                ' ', '').replace('/', '').replace('.', '').replace('-', '')))
        return self._numero

    @numero.setter
    def numero(self, value):
        if value:
            self._numero = remove_varios_espacos(remove_acentos(value.replace(
                ' ', '').replace('/', '').replace('.', '').replace('-', '')))
        else:
            self._numero = None

    class Meta:
        db_table = "proc_temp"