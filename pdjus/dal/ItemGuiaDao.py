from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.ItemGuia import ItemGuia
from util.StringUtil import remove_acentos,remove_varios_espacos, remove_links
from pdjus.modelo.Guia import Guia


class ItemGuiaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ItemGuiaDao, self).__init__(ItemGuia)

    def get_por_guia_codigo_descricao_qtd_valor_destinacao(self,guia,codigo,descricao,qtd,valor,destinacao):

        codigo = remove_links(remove_varios_espacos(remove_acentos(codigo.upper())))
        descricao = remove_links(remove_varios_espacos(remove_acentos(descricao.upper())))
        destinacao = remove_links(remove_varios_espacos(remove_acentos(destinacao.upper())))
        return self._session.query(self._classe).join(self._classe.guia).filter((Guia.id == guia.id),(self._classe._codigo == codigo), (self._classe._descricao == descricao),
                                                         (self._classe.quantidade == qtd), (self._classe.valor == valor),
                                                         (self._classe._destinacao == destinacao)).first()

