from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ItemGuiaDao import ItemGuiaDao
from pdjus.modelo.ItemGuia import ItemGuia
from pdjus.service.BaseService import BaseService


class ItemGuiaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ItemGuiaService, self).__init__(ItemGuiaDao())

    def preenche_itens_guia(self, lista_itens_guia ,guia):
        for item in lista_itens_guia:
            self.preenche_item_guia(guia ,item['codigo'],item['descricao'] ,item['quantidade'],item['valor'],item['destinacao'])

    def preenche_item_guia(self,guia , codigo, descricao, quantidade, valor,destinacao):
        if type(valor) is str:
            valor = float(valor.replace('.','').replace(',' ,'.'))
        itemGuia = self.dao.get_por_guia_codigo_descricao_qtd_valor_destinacao(guia ,codigo, descricao, quantidade, valor,destinacao)
        if not itemGuia:
            itemGuia = ItemGuia()
            itemGuia.guia = guia
            itemGuia.codigo = codigo
            itemGuia.descricao = descricao
            itemGuia.quantidade = quantidade
            itemGuia.valor = valor
            itemGuia.destinacao = destinacao
            self.salvar(itemGuia)
        return itemGuia