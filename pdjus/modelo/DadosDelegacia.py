__author__ = 'B265697367'

from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Municipio import Municipio

class DadosDelegacia(BaseClass):
    id = PrimaryKeyField(null = False)
    processo = ForeignKeyField(Processo)
    municipio = ForeignKeyField(Municipio)
    _documento = CharField(db_column = 'documento')
    _numero = CharField(db_column = 'numero')
    _distrito_policial = CharField(db_column = 'distrito_policial')

    def __init__(self,*args, **kwargs):
        self.init_on_load(*args, **kwargs)
    
    def init_on_load(self,*args, **kwargs):
        super(DadosDelegacia, self).__init__([
                                        "processo", 
                                        "municipio",
                                        "documento",
                                        "numero",
                                        "distrito_policial"],
                                        *args, **kwargs)
    
    def is_valido(self):
        """O que deve ser validado aqui?
        
        Returns:
            [Boolean] -- True para dados corretos
        """
        return True

    @property
    def documento(self):
        self._documento = remove_varios_espacos(\
                        remove_acentos(self._documento.upper()))
        return self._documento

    @documento.setter
    def documento(self, value):
        self._documento = remove_varios_espacos(\
                            remove_acentos(value.upper()))

    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, value):
        self._numero = value

    @property
    def distrito_policial(self):
        self._distrito_policial = remove_acentos(\
                                    self._distrito_policial.upper())
        return self._distrito_policial

    @distrito_policial.setter
    def distrito_policial(self, value):
        self._distrito_policial = remove_acentos(value.upper())

    class Meta:
        db_table = "dados_delegacia"
