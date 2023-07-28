
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.Processo import Processo

class Cda(BaseClass):
    id = PrimaryKeyField(null=False)
    _texto = TextField(db_column="texto")
    processo = ForeignKeyField(Processo, null=True, related_name="cdas")


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Cda, self).__init__(["texto", "processo"],*args, **kwargs)

    @property
    def texto(self):
        if self._texto:
            self._texto = remove_links(remove_varios_espacos(remove_acentos(self._texto.upper())))
        return self._texto

    @texto.setter
    def texto(self, value):
        self._texto = remove_links(remove_varios_espacos(remove_acentos(value.upper())))

    def is_valido(self):
        if not self.processo:
            print('ERRO CDA NÃO TEM PROCESSO!!')
            return False
        return True