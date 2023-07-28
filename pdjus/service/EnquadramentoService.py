from pdjus.conexao.Conexao import Singleton
from pdjus.dal.EnquadramentoDao import EnquadramentoDao
from pdjus.modelo.Enquadramento import Enquadramento
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos

class EnquadramentoService(BaseService,metaclass=Singleton):
    def __init__(self):
        super(EnquadramentoService, self).__init__(EnquadramentoDao())

    def preenche_enquadramento(self, nome):
        enquadramento = None

        nome = remove_varios_espacos(remove_acentos(nome.strip()))

        if nome != '':
            enquadramento = self.dao.get_por_nome(nome)
            if not enquadramento:
                enquadramento = Enquadramento()
                enquadramento.nome = nome
                self.salvar(enquadramento)

        return enquadramento

