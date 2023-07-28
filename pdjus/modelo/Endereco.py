
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Estado import Estado
from util.StringUtil import remove_acentos, remove_varios_espacos

class Endereco(BaseClass):
    id = PrimaryKeyField(null=False)
    _rua =  CharField(db_column="rua")
    _numero =  CharField(db_column="numero")
    _complemento =  CharField(db_column="complemento")
    _bairro =  CharField(db_column="bairro")
    _cidade =  CharField(db_column="cidade")
    cep =  CharField(db_column="cep")
    latitude = FloatField()
    longitude = FloatField()

    estado = ForeignKeyField(Estado,null=True)

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Endereco, self).__init__(["cep","numero","complemento","cidade"],*args, **kwargs)

    def is_valido(self):
        return True

    @property
    def rua(self):
        try:
            self._rua = remove_varios_espacos(remove_acentos(self._rua.upper()))
            return self._rua
        except:
            return None

    @rua.setter
    def rua(self, value):
        if value is None:
            self._rua = None
        else:
            self._rua = remove_varios_espacos(remove_acentos(value.upper()))
        
        
    @property
    def numero(self):
        try:
            self._numero = remove_varios_espacos(remove_acentos(self._numero.upper()))
            return self._numero
        except:
            return None

    @numero.setter
    def numero(self, value):
        if value is None:
            self._numero = None
        else:
            self._numero = remove_varios_espacos(remove_acentos(value.upper()))
        
    
    @property
    def complemento(self):
        try:
            self._complemento = remove_varios_espacos(remove_acentos(self._complemento.upper()))
            return self._complemento
        except:
            return None

    @complemento.setter
    def complemento(self, value):
        if value is None:
            self._complemento = None
        else:
            self._complemento = remove_varios_espacos(remove_acentos(value.upper()))
        
    @property
    def bairro(self):
        try:
            self._bairro = remove_varios_espacos(remove_acentos(self._bairro.upper()))
            return self._bairro
        except:
            return None

    @bairro.setter
    def bairro(self, value):
        if value is None:
            self._bairro = None
        else:
            self._bairro = remove_varios_espacos(remove_acentos(value.upper()))
    
    @property
    def cidade(self):
        try:
            self._cidade = remove_varios_espacos(remove_acentos(self._cidade.upper()))
            return self._cidade
        except:
            return None

    @cidade.setter
    def cidade(self, value):
        if value is None:
            self._cidade = None
        else:
            self._cidade = remove_varios_espacos(remove_acentos(value.upper()))


    def __repr__(self):
        return '{rua}, {numero}, {comp}, {bairro}, {cidade} - {estado} - ' \
               'CEP: {cep} - Lat: {lat}, Long: {lng}'.format(rua=self.rua, numero=self.numero, comp=self.complemento,
                                                             bairro=self.bairro, cidade=self.cidade, estado=self.estado,
                                                             cep=self.cep, lat=str(self.latitude),
                                                             lng=str(self.longitude))
