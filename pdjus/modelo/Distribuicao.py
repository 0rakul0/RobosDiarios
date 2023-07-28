# -*- coding: utf-8 -*-
import re
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.Caderno import Caderno
from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.Estado import Estado
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Comarca import Comarca
import datetime


class Distribuicao(BaseClass):
    id = PrimaryKeyField(null=False)
    numero_distribuicao = TextField()
    data_distribuicao = DateTimeField()
    tipo_distribuicao = TextField()
    _numero_processo = TextField(db_column="numero_processo")
    vara = TextField()
    outros = TextField()

    caderno = ForeignKeyField(Caderno,null=True)

    estado = ForeignKeyField(Estado,null=True)

    classe_processual = ForeignKeyField(ClasseProcessual,null=True)

    dado_extraido = ForeignKeyField(DadoExtraido,null=True)

    comarca = ForeignKeyField(Comarca,null= True)

    processo = ForeignKeyField(Processo, null=True,related_name="distribuicoes")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Distribuicao, self).__init__(["numero_processo","comarca","classe_processual","partes"],*args, **kwargs)

    def is_valido(self):
        if not self.numero_processo:
            print("Não pode existir um Distribuicao sem numero processo!")
            return False
        if not self.classe_processual:
            print("Não pode existir um Distribuicao sem classe processual!")
            return False
        return True


    @classmethod
    def formata_numero_processo(self, value):
        return remove_varios_espacos(remove_acentos(value.replace(
            ' ', '').replace('/', '').replace('.', '').replace('-', '')))

    @property
    def numero_processo(self):
        if self._numero_processo:
            self._numero_processo = self.formata_numero_processo(self._numero_processo)
        return self._numero_processo

    @numero_processo.setter
    def numero_processo(self, value):
        if value:
            self._numero_processo = self.formata_numero_processo(value)
        else:
            self._numero_processo = None

    @classmethod
    def is_npu(self,npu):
        regex_npu = re.compile('\d{7}\-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}', re.MULTILINE)
        return not regex_npu.match(npu) == None

    @classmethod
    def formata_npu_com_pontos(self,npu):
        if npu:
            npu = npu[:7] + '-' + npu[7:9] + '.' + npu[9:13] + '.' + npu[13] + '.' + npu[14:16] + '.' + npu[-4:]
        return npu



