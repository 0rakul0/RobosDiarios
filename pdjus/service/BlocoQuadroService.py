from pdjus.conexao.Conexao import Singleton
from pdjus.dal.BlocoQuadroDao import BlocoQuadroDao
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.service.BaseService import BaseService


class BlocoQuadroService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(BlocoQuadroService, self).__init__(BlocoQuadroDao())

    def preenche_bloco_quadro(self,texto , texto_movimento,movimento=None, caderno=None):
        blocoQuadro = None
        if movimento:
            blocoQuadro = self.dao.get_por_movimento(movimento)
        if not blocoQuadro:
            blocoQuadro = self.dao.get_por_texto(texto)

        if not blocoQuadro:
            blocoQuadro = BlocoQuadro()
            blocoQuadro.texto = texto
            blocoQuadro.texto_limpo = texto_movimento
            blocoQuadro.movimento = movimento
            blocoQuadro.caderno = caderno
            self.salvar(blocoQuadro, commit=False)

        return blocoQuadro