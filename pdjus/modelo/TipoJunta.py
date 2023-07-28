from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos

class TipoJunta(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome  # assim que setar o nome, já vai corrigí-lo

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um TipoParte sem nome!")
            return False
        return True

    class Meta:
        db_table = "tipo_junta"

