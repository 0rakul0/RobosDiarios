
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *


class Advogado(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    _numero_oab = CharField(db_column="numero_oab", unique=True)

    # partes_processos = []
    # partes_distribuicoes = []

    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Advogado, self).__init__("numero_oab",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um advogado sem nome!")
            return False
        if not self.nome and not self.numero_oab:
            print("Não pode existir um advogado sem nome e oab!")
            return False

        return True

    # @property
    # def partes_processos(self):
    #     if len(self._partes_processos) == 0:
    #         for advogado_parte_processo in self.advogado_partes_processo:
    #             self._partes_processos.append(advogado_parte_processo.parte_processo)
    #     return self._partes_processos
    #
    # @property
    # def partes_distribuicoes(self):
    #     if len(self._partes_distribuicoes) == 0:
    #         for advogado_parte_distribuicao in self.advogado_partes_distribuicao:
    #             self._partes_distribuicoes.append(advogado_parte_distribuicao.parte_distribuicao)
    #     return self._partes_distribuicoes


    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    @property
    def numero_oab(self):
        if self._numero_oab:
            self._numero_oab = self._numero_oab.upper().replace(' ','')
        return self._numero_oab

    @numero_oab.setter
    def numero_oab(self, value):
        if value:
            self._numero_oab = value.upper().replace(' ','')



