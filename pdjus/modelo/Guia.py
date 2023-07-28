import re
from datetime import datetime
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links

class Guia(BaseClass):
    __tablename__ = 'guia'
    id = PrimaryKeyField(null=False)

    _numero_guia = CharField(db_column="numero_guia")

    valor = CharField()

    data_emissao = DateField()

    _data_pagamento = DateField(db_column='data_pagamento')

    processo = ForeignKeyField(Processo,null=True,related_name="guias")

    _pagante = CharField(db_column="pagante")

    _autenticacao =  CharField(db_column="autenticacao")

    cheque_sem_fundo = BooleanField()

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um Guia sem processo!")
            return False
        return True


    @property
    def numero_guia(self):
        if self._numero_guia:
            self._numero_guia = remove_links(remove_varios_espacos(remove_acentos(self._numero_guia.upper())))
        return self._numero_guia

    @numero_guia.setter
    def numero_guia(self, value):
        if value:
            self._numero_guia = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def data_pagamento(self):
        return self._data_pagamento

    @data_pagamento.setter
    def data_pagamento(self, value):
        if value and type(value) is str and re.search('\\d{2}\/\\d{2}\/\\d{4}', value):
            data = datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')
            self._data_pagamento = data
        else:
            self._data_pagamento = value

    @property
    def pagante(self):
        if self._pagante:
            self._pagante = remove_links(remove_varios_espacos(remove_acentos(self._pagante.upper())))
        return self._pagante

    @pagante.setter
    def pagante(self, value):
        if value:
            self._pagante = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def autenticacao(self):
        if self._autenticacao:
            self._autenticacao = remove_links(remove_varios_espacos(remove_acentos(self._autenticacao.upper())))
        return self._autenticacao

    @autenticacao.setter
    def autenticacao(self, value):
        if value:
            self._autenticacao = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

