# -*- coding: utf-8 -*-
import traceback

from pdjus.modelo.Caderno import Caderno
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Diario import Diario
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
import re

class Arquivo(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome_arquivo = CharField(db_column="nome_arquivo")
    diario = ForeignKeyField(Diario,null=True, related_name="arquivos")
    caderno = ForeignKeyField(Caderno, null=True)
    _nome_original = CharField(db_column="nome_original")
    _nome_extracao = CharField(db_column="nome_extracao")
    tamanho = CharField()

    #status_baixado = DateTimeField()
    #status_convertido = DateTimeField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Arquivo, self).__init__("nome_arquivo",*args, **kwargs)

    def is_valido(self):
        if not self.nome_arquivo:
            print("Não pode existir um arquivo sem nome!")
            return False

        if not self.nome_extracao:
            print("Não pode existir um arquivo sem nome extracao!")
            raise InvalidOperation("Erro:" + traceback.format_exc())

        if not re.search("\.\w{3,4}\\b",self.nome_extracao):
            print("Não pode existir um arquivo sem a extensão no nome extracao! ex: DJSP_2019_06_20.TXT")
            raise InvalidOperation("Erro:" + traceback.format_exc())

        if not self.diario:
            print("Não pode existir um arquivo sem diario!")
            return False

        return True

    @property
    def nome_arquivo(self):
        value = self._nome_arquivo
        if value:
            if ".txt" in value:
                self.nome_extracao = value
                value = os.path.splitext(value)[0]
            elif re.search("\.\w{3}\\b", value):
                self.nome_original = value
                value = os.path.splitext(value)[0]
        self._nome_arquivo = value
        return self._nome_arquivo

    @nome_arquivo.setter
    def nome_arquivo(self, value):
        if value:
            if ".txt" in value:
                self.nome_extracao = value
                value = os.path.splitext(value)[0]
            elif re.search("\.\w{3}\\b",value):
                self.nome_original = value
                value = os.path.splitext(value)[0]
        self._nome_arquivo = value

    @property
    def nome_original(self):
        return self._nome_original if self._nome_original else self.nome_arquivo

    @nome_original.setter
    def nome_original(self, value):
        self._nome_original = value

    @property
    def nome_extracao(self):
        return self._nome_extracao if self._nome_extracao else self.nome_original

    @nome_extracao.setter
    def nome_extracao(self, value):
        self._nome_extracao = value

