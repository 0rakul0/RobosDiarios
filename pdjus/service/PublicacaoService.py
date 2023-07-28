from pdjus.conexao.Conexao import Singleton
from pdjus.dal.PublicacaoDao import PublicacaoDao
from pdjus.modelo.Publicacao import Publicacao
from pdjus.service.BaseService import BaseService


class PublicacaoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(PublicacaoService, self).__init__(PublicacaoDao())

    def preenche_publicacao(self, numero_processo, dt_pub, texto, assunto, classe, comarca, caderno):
        publicacao = Publicacao()
        publicacao.numero_processo = numero_processo
        publicacao.classe_processual = classe
        publicacao.assunto = assunto
        publicacao.caderno = caderno
        publicacao.data_publicacao = dt_pub
        publicacao.texto = texto
        publicacao.comarca = comarca
        self.salvar(publicacao,caderno)