from pdjus.conexao.Conexao import Singleton
from pdjus.dal.QuadroCredorDao import QuadroCredorDao
from pdjus.modelo.QuadroCredor import QuadroCredor
from pdjus.service.BaseService import BaseService


class QuadroCredorService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(QuadroCredorService, self).__init__(QuadroCredorDao())

    def preenche_quadro_credor(self,processo,nome,data,tipo_moeda,valor,classe_credor,fonte_dado,tag, blocoQuadro=None):
        if blocoQuadro:
            credor = self.dao.get_por_processo_nome_data_moeda_valor_classe_credor_fonte_bloco(
                processo, nome, data,
                tipo_moeda, valor, classe_credor, fonte_dado,blocoQuadro)
        else:
            credor = self.dao.get_por_processo_nome_data_moeda_valor_classe_credor_fonte(
                processo, nome, data,
                tipo_moeda, valor, classe_credor, fonte_dado)
        if not credor:
            credor = QuadroCredor()
            credor.classe_credor = classe_credor
            credor.nome = nome
            credor.data = data
            credor.processo = processo
            credor.tipo_moeda = tipo_moeda
            credor.valor = valor
            credor.bloco_quadro = blocoQuadro
            credor.fonte_dado = fonte_dado
            self.salvar(credor,tag=tag,commit=False)

        return credor