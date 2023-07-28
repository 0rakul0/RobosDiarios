from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Endereco import Endereco
from util.StringUtil import remove_acentos, remove_varios_espacos

class EnderecoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(EnderecoDao, self).__init__(Endereco)

    def get_por_dados(self, rua, numero, cidade):
        try:
            if numero is not None:
                numero = remove_acentos(remove_varios_espacos(numero.upper()))

            if rua is not None:
                rua = remove_acentos(remove_varios_espacos(rua.upper()))

            if cidade is not None:
                cidade = remove_acentos(remove_varios_espacos(cidade.upper()))


            return self._classe.get(self._classe._rua == rua,
                                                        self._classe._numero == numero,
                                                        self._classe._cidade == cidade)
        except self._classe.DoesNotExist as e:
            return None

    def get_cidade(self, cidade):
        try:
            if cidade is not None:
                cidade = remove_acentos(remove_varios_espacos(cidade.upper()))


                return self._classe.get(self._classe._rua == None,
                                                            self._classe._complemento == None,
                                                            self._classe._numero == None,
                                                            self._classe.cep == None,
                                                            self._classe._bairro == None,
                                                            self._classe._cidade == cidade)
        except self._classe.DoesNotExist as e:
            return None