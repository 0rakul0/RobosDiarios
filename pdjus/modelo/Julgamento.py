from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Juiz import Juiz


class Julgamento(BaseClass):
    id = PrimaryKeyField(null=False)
    _tipo_participante = CharField(db_column="tipo_participante", null=False)
    processo = ForeignKeyField(Processo,null=False)
    juiz = ForeignKeyField(Juiz,null=False)

    def __init__(self, *args, **kwargs):
        self.init_on_load(*args, **kwargs)

    def init_on_load(self, *args, **kwargs):
        super(Julgamento, self).__init__("nome", *args, **kwargs)

    def is_valido(self):
        if not self.juiz or not self.processo or not self.tipo_participante:
            print("Não pode existir um julgamento sem os campos de juiz,processo e tipo participante!")
            return False
        return True

    @property
    def tipo_participante(self):
        if self._tipo_participante:
            self._tipo_participante = remove_varios_espacos(remove_acentos(self._tipo_participante.upper()))
        return self._tipo_participante

    @tipo_participante.setter
    def tipo_participante(self, value):
        if value:
            self._tipo_participante = remove_varios_espacos(remove_acentos(value.upper()))