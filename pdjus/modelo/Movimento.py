
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.Processo import Processo
from pdjus.modelo.TipoMovimento import TipoMovimento
import hashlib


class Movimento(BaseClass):
    id = PrimaryKeyField(null=False)
    data = DateTimeField()

    _texto =  TextField(db_column="texto")

    processo = ForeignKeyField(Processo,null=True, related_name="movimentos")

    tipo_movimento = ForeignKeyField(TipoMovimento,null=True)

    _hash_texto = TextField(db_column="hash_texto")

    _observacao = TextField (db_column="observacao")

    # situacao = ForeignKeyField(Situacao,null=True,related_name="movimentos")

    # nota_expediente = ForeignKeyField(NotaExpediente", uselist=False, backref="nota_expediente")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Movimento, self).__init__(["texto","processo","data"],*args, **kwargs)

    def is_valido(self):
        if not self.texto or not self.texto.strip():
            self.texto = None
        if not self.processo:
            print("Não pode existir um Movimento sem processo!")
            return False
        return True

    @property
    def texto(self):
        if self._texto:
            self._texto = remove_links(remove_varios_espacos(remove_acentos(self._texto.upper())))
        return self._texto

    @texto.setter
    def texto(self, value):
        if value:
            self._texto = remove_links(remove_varios_espacos(remove_acentos(value.upper())))
            self._hash_texto = hashlib.md5(self._texto.encode('utf-8')).hexdigest()
        else:
            self._texto = None

    @property
    def observacao(self):
        if self._observacao:
            self._observacao = remove_links (remove_varios_espacos (remove_acentos (self._observacao.upper())))
        return self._observacao

    @property
    def marcadores(self):
        self._marcadores = []
        for movimento_marcador in self.movimento_marcadores:
            self._marcadores.append(movimento_marcador.marcador)
        return self._marcadores

    @observacao.setter
    def observacao(self, value):
        if value:
            self._observacao = remove_links (remove_varios_espacos (remove_acentos (value.upper())))
        else:
            self._observacao = None