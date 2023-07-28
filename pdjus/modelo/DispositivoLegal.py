__author__ = 'B249025230'
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *

class DispositivoLegal(BaseClass):
    id = PrimaryKeyField(null=False)
    artigo = CharField()
    paragrafo = CharField()
    inciso = CharField()
    alinea = CharField()
    item = CharField()
    parte = CharField()
    livro = CharField()
    titulo = CharField()
    capitulo = CharField()
    secao = CharField()
    subsecao = CharField()
    _lei =  CharField(db_column="lei")
    _nome = ''

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(DispositivoLegal, self).__init__(*args, **kwargs)

    def is_valido(self):
        return True

    @property
    def lei(self):
        self._nome = remove_varios_espacos(remove_acentos(self._lei.upper()))
        return self._lei

    @lei.setter
    def lei(self, value):
        self._lei = remove_varios_espacos(remove_acentos(value.upper()))

    class Meta:
        db_table = "dispositivo_legal"