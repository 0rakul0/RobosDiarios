from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ComarcaDao import ComarcaDao
from pdjus.modelo.Comarca import Comarca
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos


class ComarcaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ComarcaService, self).__init__(ComarcaDao())

    def preenche_comarca(self, nome_comarca=None, tribunal=None,codigo_comarca = None):
        comarca = None
        if nome_comarca:
            nome_comarca = remove_acentos(remove_varios_espacos(nome_comarca.strip().upper()))
            if tribunal:
                comarca = self.dao.get_por_nome_comarca_e_tribunal(nome_comarca, tribunal)
                if not comarca:
                    comarca = self.dao.get_por_nome_comarca(nome_comarca)
                    if comarca and not comarca.tribunal == tribunal:
                        comarca.tribunal = tribunal
                        self.salvar(comarca)
            else:
                comarca = self.dao.get_por_nome_comarca(nome_comarca)
        elif codigo_comarca:
            if tribunal:
                comarca = self.dao.get_por_nome_comarca_e_tribunal(codigo_comarca, tribunal)

        if comarca is None:
            comarca = Comarca()
            comarca.nome = nome_comarca
            comarca.codigo_comarca = codigo_comarca
            comarca.tribunal = tribunal
            self.salvar(comarca)

        return comarca