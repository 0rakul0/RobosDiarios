# -*- coding: utf-8 -*-

from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.Diario import Diario
import re


class Caderno(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome =  CharField(db_column="nome")
    paginas = IntegerField()
    documentos = IntegerField()
    diario = ForeignKeyField(Diario,null=True, related_name="cadernos")

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Caderno, self).__init__(["nome","diario"],*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Caderno sem nome!")
            return False
        if not self.diario:
            print("Não pode existir um Caderno sem diario!")
            return False

        return True

    @property
    def nome(self):
        if self._nome is not None:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
            return self._nome
        else:
            return None

    @nome.setter
    def nome(self, value):
        if value is not None:
            self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    @classmethod
    def get_nome_caderno(self,nome_arquivo,diario):
        if diario.nome == "DJSP":
            return Caderno._get_nome_caderno_DJSP(nome_arquivo)
        else:
            if 'JUD' in nome_arquivo:
                return "JUDICIAL"
            elif 'ADM' in nome_arquivo:
                return 'ADMINISTRATIVO'
            else:
                return re.search('^\w+?_(.*?)_', nome_arquivo).group(1)

    @classmethod
    def _get_nome_caderno_DJSP(self,nome_arquivo):
        if 'Caderno10' in nome_arquivo:
            return "ADMINISTRATIVO"
        elif 'Caderno11' in nome_arquivo:
            return "JUDICIAL - 2a INSTANCIA"
        elif 'Caderno12' in nome_arquivo:
            return "JUDICIAL - 1a INSTANCIA - CAPITAL"
        elif 'Caderno14' in nome_arquivo:
            return "EDITAIS E LEILÕES"
        elif 'Caderno18' in nome_arquivo:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE I"
        elif 'Caderno13' in nome_arquivo:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE II"
        elif 'Caderno15' in nome_arquivo:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE III"
        elif 'Judiciario_III' in nome_arquivo:
            return "JUDICIARIO III - 1a INSTANCIA - INTERIOR"
        elif 'Judiciario_II' in nome_arquivo:
            return "JUDICIARIO II - 1a INSTANCIA - CAPITAL"
        elif 'Edita' in nome_arquivo:
            return "EDITAL - 1a INSTANCIA"
        elif "Suplemento" in nome_arquivo:
            return "SUPLEMENTOS - DIARIO ANTIGO"
        elif "Empresarial" in nome_arquivo:
            return "EMPRESARIAL"
        elif "Executivo" in nome_arquivo:
            return "EXECUTIVO - DIARIO ANTIGO"
        elif "Ineditoriais" in nome_arquivo:
            return "INEDITORIAIS - DIARIO ANTIGO"
        elif 'Judiciario_I' in nome_arquivo:
            return "JUDICIAL - DIARIO ANTIGO - PARTE I"
        elif 'Judiciario_II' in nome_arquivo:
            return "JUDICIAL - DIARIO ANTIGO - PARTE II"
        elif 'Judiciario_III' in nome_arquivo:
            return "JUDICIAL - DIARIO ANTIGO - PARTE III"

    @classmethod
    def get_cod_caderno(self, caderno):
        if not caderno or not caderno.diario:
            return None
        elif caderno.diario.nome == "DJSP":
            return Caderno._get_cod_caderno_DJSP(caderno)

    @classmethod
    def _get_cod_caderno_DJSP(self,caderno):
        if caderno.startswith("JUDICIAL") and caderno.endswith("CAPITAL"):
            return 12
        elif caderno.endswith("PARTE I"):
            return 18
        elif caderno.endswith("PARTE II"):
            return 13
        elif caderno.endswith("PARTE III"):
            return 15
        elif caderno.startswith("JUDICIARIO III"):
            return 3
        elif caderno.startswith("JUDICIARIO II"):
            return 2