import html
import re
from pdjus.conexao.Conexao import Singleton
from pdjus.dal.EmpresaDao import EmpresaDao
from pdjus.dal.EmpresaObjetoSocialDao import EmpresaObjetoSocialDao
from pdjus.dal.EmpresaEnquadramentoDao import EmpresaEnquadramentoDao
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.EmpresaObjetoSocial import EmpresaObjetoSocial
from pdjus.modelo.EmpresaEnquadramento import EmpresaEnquadramento
from pdjus.service.BaseService import BaseService
from pdjus.service.ObjetoSocialService import ObjetoSocialService
from pdjus.service.EnquadramentoService import EnquadramentoService
from pdjus.service.ParteProcessoService import ParteProcessoService
from pdjus.service.ParteService import ParteService
from util.ConfigManager import ConfigManager
from util.StringUtil import remove_varios_espacos, remove_pontuacao,remove_caracteres_especiais


class EmpresaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(EmpresaService, self).__init__(EmpresaDao())

    def preenche_empresa(self,cnpj, nome=None, soma_ocorrencias = None):
        cnpj = Empresa.formata_cnpj(cnpj)
        empresa = self.dao.get_por_cnpj(cnpj)
        if not empresa:
            empresa = Empresa()
        empresa.cnpj = cnpj
        if empresa.quantidade_ocorrencias and soma_ocorrencias:
            empresa.quantidade_ocorrencias += 1
        elif not empresa.quantidade_ocorrencias:
            empresa.quantidade_ocorrencias = 1
        empresa.nome = nome
        self.salvar(empresa)

        return empresa

    def preenche_empresa_por_nome(self,nome,nire=None):
        empresa = self.dao.get_por_nome(nome)
        if not empresa:
            empresa = Empresa()
            if 'SITUADA' in nome:
                try:
                    nome = re.search('(.*) SITUADA A.*$', nome).group(1)
                except:
                    pass
            remove_caracteres_especiais(remove_pontuacao(remove_varios_espacos(nome)))
            empresa.nire = nire
            empresa.nome = nome
            self.salvar(obj=empresa,salvar_estrangeiras = False,salvar_many_to_many = False)
        return empresa

    def preenche_empresa_por_nire(self,nome,nire):
        empresa = self.dao.get_por_nire(nire)
        if not empresa:
            empresa = Empresa()
            nome = remove_caracteres_especiais(remove_pontuacao(remove_varios_espacos(re.sub('(?![A-Z])(?! )-(?! )','',nome))))
            empresa.nire = nire.strip()
            empresa.nome = nome.strip()
            self.salvar(obj=empresa,salvar_estrangeiras = False,salvar_many_to_many = False)
        return empresa


    def seta_objeto_social(self, empresa, nome,fonte_dado,principal=False,lista_cnae = None,cnae=None):
        objetoSocialService = ObjetoSocialService()
        if empresa:
            empresa_objeto_socialdao = EmpresaObjetoSocialDao()
            objeto_social = objetoSocialService.preenche_objeto_social(nome,lista_cnae,cnae)
            empresa_objeto_social = empresa_objeto_socialdao.get_por_empresa_objeto_social(empresa,objeto_social)
            if not empresa_objeto_social:
                empresa_objeto_social = EmpresaObjetoSocial()
            if principal:
                objetos = empresa_objeto_socialdao.listar_objetos_da_empresa(empresa)
                if len(objetos) > 0:
                    if len(list(filter(lambda objeto: objeto.principal == True, objetos))) > 0:
                        principal = False
            # if fonte_dado == 1:
            #     principal = True
            empresa_objeto_social.empresa = empresa
            empresa_objeto_social.objeto_social = objeto_social
            empresa_objeto_social.principal = principal
            empresa_objeto_social.fonte_dado = fonte_dado
            empresa_objeto_socialdao.salvar(empresa_objeto_social)

    def seta_enquadramento(self, empresa, nome):
        enquadramentoService = EnquadramentoService()
        if empresa:
            empresa_enquadramentodao = EmpresaEnquadramentoDao()
            enquadramento = enquadramentoService.preenche_enquadramento(nome)
            empresa_enquadramento = empresa_enquadramentodao.get_por_empresa_enquadramento(empresa,enquadramento)

            if not empresa_enquadramento:
                empresa_enquadramento = EmpresaEnquadramento()
                empresa_enquadramento.empresa = empresa
                empresa_enquadramento.enquadramento = enquadramento
                empresa_enquadramentodao.salvar(empresa_enquadramento)

    def seta_processo(self,empresa,processo):
        parte_service = ParteService()
        encontrou_empresa = False
        for parte in processo.partes:
            # HTML ESCAPE USADO PARA TRATAR O CASO DO &AMP; Coloquei isso pq o escape de algo já escaped só acrescenta mais o &AMP; então pode acusar um falso negativo
            if html.escape(empresa.nome).upper() == parte.nome or empresa.nome == parte.nome or \
                    remove_varios_espacos(remove_pontuacao(parte.nome)) == remove_varios_espacos(remove_pontuacao(empresa.nome)):
                encontrou_empresa = True
                parte.empresa = empresa
                ConfigManager().escreve_log(
                    "Criada relação entre parte {} do processo {} e CNPJ {}.".format(parte.nome, processo.npu,
                                                                                     empresa.cnpj))
                parte_service.salvar(parte)
        if not encontrou_empresa:
            for parte in processo.partes:
                # SE NÃO ENCONTROU A EMPRESA, VERIFICAR SE A EMPRESA FAZ PARTE DO NOME DA PARTE.. PODE TER ERRO NA SEPARAÇÃO
                # DO NOME DA PARTE COM O SÍNDICO POR EXEMPLO ENTÃO VERIFICO ISSO COM O IN AO INVÉS DO ==
                if html.escape(empresa.nome).upper() in parte.nome or empresa.nome in parte.nome or \
                        remove_varios_espacos(remove_pontuacao(empresa.nome)) in remove_varios_espacos(remove_pontuacao(parte.nome)):
                    encontrou_empresa = True
                    parte.empresa = empresa
                    ConfigManager().escreve_log(
                        "Criada relação entre parte {} com a empresa {} do processo {} e CNPJ {}.".format(parte.nome,
                                                                                                          empresa.nome,
                                                                                                          processo.npu,
                                                                                                          empresa.cnpj))
                    parte_service.salvar(parte)
            if not encontrou_empresa:
                ConfigManager().escreve_log(
                    "PROBLEMA: Não foi possível encontrar a empresa {} na lista de partes do processo {} para inserir o CNPJ {}.".format(
                        empresa.nome, processo.npu, empresa.cnpj))


