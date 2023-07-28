
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.Rais import Rais
from util.StringUtil import corrige_nome, abrevia_nome
from pdjus.modelo.PessoaFisica import PessoaFisica


class Parte(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome =  CharField(db_column="nome")
    empresa = ForeignKeyField(Empresa,null=True)
    pessoa_fisica = ForeignKeyField(PessoaFisica, null=True)
    rais = ForeignKeyField(Rais,null=True)
    _nome_corrigido =  CharField(db_column="nome_corrigido")
    _nome_abreviado =  CharField(db_column="nome_abreviado")
    pessoa_juridica = BooleanField()
    #genero = CharField(db_column="genero")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Parte, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Parte sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome #assim que setar o nome, já vai corrigí-lo

    @property
    def nome_corrigido(self):
        self._nome_corrigido = remove_varios_espacos(remove_acentos(self._nome_corrigido.upper()))
        return self._nome_corrigido

    @nome_corrigido.setter
    def nome_corrigido(self, value):
        self._nome_corrigido = corrige_nome(remove_varios_espacos(remove_acentos(value.upper())))
        self.nome_abreviado = self._nome_corrigido #assim que corrigir o nome, já vai abreviá-lo

    @property
    def nome_abreviado(self):
        self._nome_abreviado = remove_varios_espacos(remove_acentos(self._nome_abreviado.upper()))
        return self._nome_abreviado

    @nome_abreviado.setter
    def nome_abreviado(self, value):
        self._nome_abreviado = abrevia_nome(remove_varios_espacos(remove_acentos(value.upper())))