
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.BaseClass import *

class Estado(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    sigla = CharField()

    estados_por_sigla = {"AC":"ACRE",
                        "AL":"ALAGOAS",
                        "AP":"AMAPÁ",
                        "AM": "AMAZONAS",
                        "BA": "BAHIA",
                        "CE": "CEARÁ",
                        "DF": "DISTRITO FEDERAL",
                        "ES": "ESPÍRITO SANTO",
                        "GO": "GOIÁS",
                        "MA": "MARANHÃO",
                        "MT": "MATO GROSSO",
                        "MS": "MATO GROSSO DO SUL",
                        "MG": "MINAS GERAIS",
                        "PA": "PARÁ",
                        "PB": "PARAÍBA",
                        "PR": "PARANÁ",
                        "PE": "PERNAMBUCO",
                        "PI": "PIAUÍ",
                        "RJ": "RIO DE JANEIRO",
                        "RN": "RIO GRANDE DO NORTE",
                        "RS": "RIO GRANDE DO SUL",
                        "RO": "RONDÔNIA",
                        "RR": "RORAIMA",
                        "SC": "SANTA CATARINA",
                        "SP": "SÃO PAULO",
                        "SE": "SERGIPE",
                        "TO": "TOCANTIS",
                         "TRF1": "TRIBUNAL REGIONAL FEDERAL da 1ª Região",
                         "TRF2": "TRIBUNAL REGIONAL FEDERAL da 2ª Região",
                         "TRF3": "TRIBUNAL REGIONAL FEDERAL da 3ª Região",
                         "TRF4": "TRIBUNAL REGIONAL FEDERAL da 4ª Região",
                         "TRF5": "TRIBUNAL REGIONAL FEDERAL da 5ª Região"
                         }

    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Estado, self).__init__("sigla",*args, **kwargs)



    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Estado sem nome!")
            return False
        if not self.sigla:
            print("Não pode existir um Estado sem sigla!")
            return False
        return True

    @property
    def nome(self):
        try:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
            return self._nome
        except:
            return None

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))

    def __repr__(self):
        return self.sigla