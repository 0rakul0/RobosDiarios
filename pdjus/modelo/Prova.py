
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Endereco import Endereco


class Prova(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome =  CharField(db_column="nome")
    descricao =  CharField(db_column="descricao")
    quantidade =  FloatField(db_column="quantidade")
    quantidade_bruta =  FloatField(db_column="quantidade_bruta")
    _unidade =  CharField(db_column="unidade")
    _unidade_bruta =  CharField(db_column="unidade_bruta")

    processo = ForeignKeyField(Processo,null=True,related_name="provas")

    endereco = ForeignKeyField(Endereco,null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Prova, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um Prova sem processo!")
            return False
        return True

    @property
    def nome(self):
        try:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
            return self._nome
        except:
            return None

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))


    @property
    def unidade(self):
        try:
            self._unidade = remove_varios_espacos(remove_acentos(self._unidade.upper()))
            return self._unidade
        except:
            return None

    @unidade.setter
    def unidade(self, value):
        self._unidade = remove_varios_espacos(remove_acentos(value.upper()))


    @property
    def unidade_bruta(self):
        try:
            self._unidade_bruta = remove_varios_espacos(remove_acentos(self._unidade_bruta.upper()))
            return self._unidade_bruta
        except:
            return None

    @unidade_bruta.setter
    def unidade_bruta(self, value):
        self._unidade_bruta = remove_varios_espacos(remove_acentos(value.upper()))

    def __repr__(self):
        return str(self.nome) + " - " + str(self.quantidade) + " " + str(self.unidade) + " (" + \
               str(self.quantidade_bruta) + " " + str(self.unidade_bruta) + " -- " + str(self.descricao) + \
               ") - Local: " + \
               str(self.endereco if self.endereco is not None else None)