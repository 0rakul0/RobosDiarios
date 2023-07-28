from pdjus.conexao.Conexao import Singleton
from pdjus.dal.CadernoDao import CadernoDao
from pdjus.modelo.Caderno import Caderno
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_acentos, remove_varios_espacos


class CadernoService(BaseService ,metaclass=Singleton):

    def __init__(self):
        super(CadernoService, self).__init__(CadernoDao())

    def preenche_caderno(self, nome, diario , paginas = None, documentos = None):
        nome = remove_varios_espacos(remove_acentos(nome.upper().strip()))
        caderno = self.dao.get_por_diario_e_nome(diario,nome)

        if not caderno:
            caderno = Caderno()
        caderno.nome = nome
        caderno.diario = diario
        caderno.paginas = paginas
        caderno. documentos = documentos
        self.salvar(caderno,commit=True,salvar_estrangeiras=False,salvar_many_to_many=False)

        return caderno