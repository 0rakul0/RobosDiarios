# -*- coding: utf-8 -*-

from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.Caderno import Caderno
from pdjus.modelo.Estado import Estado
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Comarca import Comarca

class Publicacao(BaseClass):
    id = PrimaryKeyField(null=False)
    data_publicacao = DateTimeField()
    numero_processo = TextField()

    caderno = ForeignKeyField(Caderno,null=True)

    classe_processual = ForeignKeyField(ClasseProcessual,null=True)

    assunto = ForeignKeyField(Assunto, null=True)

    _texto = TextField(db_column="texto")

    dado_extraido = ForeignKeyField(DadoExtraido,null=True,related_name="publicacoes")

    comarca = ForeignKeyField(Comarca,null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Publicacao, self).__init__(["data_publicacao","numero_processo","caderno_id","classe_processual_id","comarca_id"],*args, **kwargs)

    def is_valido(self):
        if not self.numero_processo:
            print("Não pode existir um Publicacao sem numero processo!")
            return False
        if not self.assunto:
            print("Não pode existir um Publicacao sem assunto!")
            return False
        return True

    @property
    def texto(self):
        if self._texto:
            self._texto = remove_varios_espacos(remove_acentos(self._texto.upper()))
        return self._texto

    @texto.setter
    def texto(self, value):
        if value:
            self._texto = remove_varios_espacos(remove_acentos(value.upper()))