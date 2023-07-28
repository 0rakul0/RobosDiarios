from pdjus.modelo.Guia import Guia

__author__ = 'B249025230'

from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links

class ItemGuia(BaseClass):
    id = PrimaryKeyField(null=False)

    _codigo = CharField(db_column="codigo")

    _descricao = CharField(db_column="descricao")

    quantidade = CharField()

    _destinacao = CharField(db_column="destinacao")

    valor = DecimalField()

    guia = ForeignKeyField(Guia,null=True,related_name="itens_guia")

    def is_valido(self):
        if not self.guia:
            print("Não pode existir um ItemGuia sem guia!")
            return False
        return True

    @property
    def codigo(self):
        if self._codigo:
            self._codigo = remove_links(remove_varios_espacos(remove_acentos(self._codigo.upper())))
        return self._codigo

    @codigo.setter
    def codigo(self, value):
        if value:
            self._codigo = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def descricao(self):
        if self._descricao:
            self._descricao = remove_links(remove_varios_espacos(remove_acentos(self._descricao.upper())))
        return self._descricao

    @descricao.setter
    def descricao(self, value):
        if value:
            self._descricao = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def destinacao(self):
        if self._destinacao:
            self._destinacao = remove_links(remove_varios_espacos(remove_acentos(self._destinacao.upper())))
        return self._destinacao

    @destinacao.setter
    def destinacao(self, value):
        if value:
            self._destinacao = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    class Meta:
        db_table = "item_guia"