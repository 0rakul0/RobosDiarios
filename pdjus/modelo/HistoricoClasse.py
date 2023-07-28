
from pdjus.modelo.Area import Area
from pdjus.modelo.BaseClass import *
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links

class HistoricoClasse(BaseClass):
    id = PrimaryKeyField(null=False)
    data = DateTimeField()

    processo = ForeignKeyField(Processo,null=True, related_name="historico_classe")

    classe_processual = ForeignKeyField(ClasseProcessual,null=True)

    area = ForeignKeyField(Area,null=True)

    _motivo =  CharField(db_column="motivo")

    _tipo =  CharField(db_column="tipo")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(HistoricoClasse, self).__init__(["data","classe_processual","processo"],*args, **kwargs)


    def is_valido(self):
        if not self.processo:
            print("Não pode existir um HistoricoClasse sem processo!")
            return False
        if not self.classe_processual:
            print("Não pode existir um HistoricoClasse sem classe_processual!")
            return False
        return True

    @property
    def motivo(self):
        if self._motivo:
            self._motivo = remove_links(remove_varios_espacos(remove_acentos(self._motivo.upper())))
        return self._motivo

    @motivo.setter
    def motivo(self, value):
        if value:
            self._motivo = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def tipo(self):
        if self._tipo:
            self._tipo = remove_links(remove_varios_espacos(remove_acentos(self._tipo.upper())))
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if value:
            self._tipo = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    class Meta:
        db_table = "historico_classe"