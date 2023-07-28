from pdjus.conexao.Conexao import Singleton
from pdjus.service.BaseService import BaseService
from pdjus.modelo.DadosDelegacia import DadosDelegacia
from pdjus.dal.DadosDelegaciaDao import DadosDelegaciaDao


class DadosDelegaciaService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(DadosDelegaciaService, self).__init__(DadosDelegaciaDao())

    def preenche_dados_delegacia(self, documento, numero, distrito, municipio,
                                 processo):

        dados_delegacia = self.dao.get_por_numero(numero)

        if not dados_delegacia:
            dados_delegacia = DadosDelegacia()
            dados_delegacia.processo = processo
            dados_delegacia.municipio = municipio
            dados_delegacia.documento = documento
            dados_delegacia.numero = numero
            dados_delegacia.distrito_policial = distrito

            self.salvar(dados_delegacia)

        return dados_delegacia