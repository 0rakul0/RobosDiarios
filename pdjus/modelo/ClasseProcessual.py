
from util.StringUtil import remove_acentos, remove_varios_espacos, corrige_nome_classe
from pdjus.modelo.BaseClass import *

class ClasseProcessual(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    _nome_corrigido = CharField(db_column='nome_corrigido')
    codigo_classe_processual = CharField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ClasseProcessual, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome and not self.codigo_classe_processual:
            print("Não pode existir um ClasseProcessual sem nome e codigo!")
            return False

        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome  # assim que setar o nome, já vai corrigí-lo

    @property
    def nome_corrigido(self):
        self._nome_corrigido = remove_varios_espacos(remove_acentos(self._nome_corrigido.upper()))
        return self._nome_corrigido

    @nome_corrigido.setter
    def nome_corrigido(self, value):
        self._nome_corrigido = corrige_nome_classe(remove_varios_espacos(remove_acentos(value.upper())))
        self.nome_abreviado = self._nome_corrigido  # assim que corrigir o nome, já vai abreviá-lo


    class Meta:
        db_table = "classe_processual"