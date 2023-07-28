from pdjus.conexao.Conexao import Singleton
from pdjus.dal.AssuntoDao import AssuntoDao
from pdjus.modelo.Assunto import Assunto
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos


class AssuntoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(AssuntoService, self).__init__(AssuntoDao())

    def preenche_assunto(self,nome_assunto, cod_assunto=None):
        assunto = None
        
        nome_assunto = remove_varios_espacos(remove_acentos(nome_assunto.strip()))

        if nome_assunto != '':
            assunto = self.dao.get_por_nome(nome_assunto)
            if not assunto:
                assunto = Assunto()
                assunto.nome = nome_assunto
                assunto.cod_assunto = cod_assunto
                self.salvar(assunto,salvar_estrangeiras=False,salvar_many_to_many=False)

        return assunto