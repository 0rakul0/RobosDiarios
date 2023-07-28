from pdjus.conexao.Conexao import Singleton
from pdjus.dal.MunicipioDao import MunicipioDao
from pdjus.modelo.Municipio import Municipio
from pdjus.service.BaseService import BaseService


class MunicipioService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(MunicipioService, self).__init__(MunicipioDao())

    def preenche_municipio(self,nome,estado,num_ibge=None):
        municipio = self.dao.get_por_nome_e_estado_e_numero_ibge(nome, estado, num_ibge)
        if not municipio:
            municipio = Municipio()
            municipio.nome = nome
            municipio.numero_ibge = num_ibge
            municipio.estado = estado
            self.salvar(municipio)
        return municipio