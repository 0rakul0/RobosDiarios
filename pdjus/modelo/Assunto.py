
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.BaseClass import *

class Assunto(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Assunto, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um assunto sem nome!")
            return False

        return True


    @property
    def nome(self):
        if self._nome:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    @classmethod
    def is_falencia_recuperacao_convolacao(self, nome):
        if not nome:
            return False
        return remove_varios_espacos (remove_acentos ('falencia'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('autofalencia'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('recuperacao'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('convolacao'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('concordata'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('credor'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('devedor'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('falimentar'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('falido'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('declaracao'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('impugnacao'.upper ())) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('habilitacao'.upper ())) in (remove_varios_espacos (remove_acentos (nome.upper ()))
                   and remove_varios_espacos (remove_acentos ('credito'.upper ()))) in remove_varios_espacos (remove_acentos (nome.upper ())) \
               or remove_varios_espacos (remove_acentos ('insolvencia'.upper ())) in (remove_varios_espacos (remove_acentos (nome.upper ()))
                   and remove_varios_espacos (remove_acentos ('civil'.upper ()))) in remove_varios_espacos (remove_acentos (nome.upper ()))

    class Meta:
        db_table = "assunto"

