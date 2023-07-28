
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos,remove_links


class ObjetoSocial(BaseClass):
    #empresaobjetosocial = EmpresaObjetoSocial()
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column="nome")
    classificado = BooleanField(db_column="classificado")
    #empresas = ManyToMany(Empresa)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ObjetoSocial, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self._nome:
            print("Não pode existir um objeto sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_links(remove_varios_espacos(remove_acentos(self._nome.upper())))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_links(remove_varios_espacos(remove_acentos(value.upper())))




    class Meta:
        db_table = "objeto_social"

