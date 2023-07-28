from util.StringUtil import remove_acentos, remove_varios_espacos,remove_links
from pdjus.modelo.BaseClass import *


class Enquadramento(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column="nome")

    def is_valido(self):
        if not self._nome:
            print("Não pode existir um enquadramento sem nome!")
            return False

        return True

    @property
    def nome(self):
        if self.nome:
            self._nome = remove_links(remove_varios_espacos(remove_acentos(self._nome.upper())))
        return self._nome

    @nome.setter
    def nome(self, value):
        if value:
            self._nome = remove_links(remove_varios_espacos(remove_acentos(value.upper())))
        else:
            self._nome = None