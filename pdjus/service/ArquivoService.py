from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ArquivoDao import ArquivoDao
from pdjus.modelo.Arquivo import Arquivo
from pdjus.service.BaseService import BaseService
from util.ConfigManager import ConfigManager

class ArquivoService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(ArquivoService, self).__init__(ArquivoDao())

    def preenche_arquivo(self, nome, diario=None, caderno=None, status_baixado=None, tamanho = None):

        updated = False
        arquivo = self.dao.get_por_nome_arquivo(nome)

        if not arquivo:
            arquivo = Arquivo()
            arquivo.nome_arquivo = nome
            arquivo.tamanho = tamanho
            updated = True

        if not arquivo.diario and diario:
            arquivo.diario = diario
            updated = True

        if not arquivo.caderno and caderno:
            arquivo.caderno = caderno
            updated = True

        # status baixado foi removido da classe arquivo
        # if not arquivo.status_baixado:
        #     arquivo.status_baixado = status_baixado

        if updated:
            self.salvar(arquivo)

        return arquivo
        
