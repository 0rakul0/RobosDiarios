from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ObjetoSocialDao import ObjetoSocialDao
from pdjus.modelo.ObjetoSocial import ObjetoSocial
from pdjus.service.BaseService import BaseService
from pdjus.service.CnaeService import CnaeService
from util.StringUtil import remove_varios_espacos, remove_acentos,remove_caracteres_especiais

class ObjetoSocialService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ObjetoSocialService, self).__init__(ObjetoSocialDao())

    def preenche_objeto_social(self,nome,lista_cnae = None, cnae=None): #lista_cnae são objetos vindo do mapa,cnae é o cnae vindo da receita federal
        objeto_social = None
        nome = remove_caracteres_especiais(remove_varios_espacos(remove_acentos(nome.strip())))
        if nome != '':
            objeto_social = self.dao.get_por_nome(nome)
            if not objeto_social:
                objeto_social = ObjetoSocial()
                objeto_social.nome = nome
                self.salvar(objeto_social)
            cnae_service = CnaeService()
            if cnae:
                cnae_service.seta_cnae(objeto_social, cnae)
            else:
                cnae_service.verifica_objeto_social_cnae(objeto_social,lista_cnae)

        return objeto_social