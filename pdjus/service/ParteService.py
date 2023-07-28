from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ParteDao import ParteDao
from pdjus.modelo.Parte import Parte
from pdjus.service.BaseService import BaseService


class ParteService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ParteService, self).__init__(ParteDao())

    def preenche_parte(self, nome_parte, pessoa=None):
        parte = Parte()
        parte.nome = nome_parte

        if pessoa:
            parte.pessoa_fisica = pessoa

        return parte