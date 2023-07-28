import re
import json,time
from pdjus.conexao.Conexao import Singleton
from datetime import datetime
from pdjus.dal.JuntaComercialDao import JuntaComercialDao
from pdjus.modelo.JuntaComercial import JuntaComercial
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais,remove_links
from classificadores.ClassificaCNAE import ClassificaCNAE
from classificadores.ClassificaJucesp import ClassificaJucesp
from pdjus.service.CnaeService import CnaeService


from pdjus.service.EmpresaService import EmpresaService

class JuntaComercialService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(JuntaComercialService, self).__init__(JuntaComercialDao())

    def preenche_junta_comercial(self,nome_empresa,nire,tipo,data,data_caderno,texto,numero_alteracao=None,regex_util = None):
        empresa_service = EmpresaService()
        classifica_jucesp = ClassificaJucesp()
        empresa = empresa_service.preenche_empresa_por_nire(nome_empresa,nire)

        texto = remove_caracteres_especiais(remove_varios_espacos(remove_acentos(texto))).upper()
        if not empresa._cnpj:
            try:
                if 'INCLUSAO DE CGC' in texto:
                    cnpj = re.search('\d{2}\.?\d{3}\.?\d{3}\/?\d{4}\-?\d{2}', texto).group(0)
                    empresa._cnpj = empresa.formata_cnpj(cnpj)
                    empresa_service.salvar(empresa)

                if not empresa._cnpj:
                    cnpj,enquadramento,endereco,cep = self.extrai_json_mapa(nome_empresa,nire)
                    if cnpj:
                        empresa._cnpj = empresa.formata_cnpj(cnpj)
                    if enquadramento:
                        empresa_service.seta_enquadramento(empresa,enquadramento)
                    if endereco:
                        empresa.endereco = endereco
                    if cep:
                        empresa.cep = cep
                    empresa_service.salvar(empresa)
            except:
                print("Não foi possível extrair o CNPJ")

        if re.search("CONSTITUICOES",tipo.nome): #Seta o objeto social da empresa e trata o cnae
            empresa_service.seta_objeto_social(empresa,texto,'1',True)

        if type(data) != datetime:
            data = datetime.strptime(data, "%d/%m/%Y").date()

        junta_comercial = self.dao.get_por_empresa_tipo_data_e_texto(empresa, tipo, data, texto)
        if not junta_comercial:
            junta_comercial = JuntaComercial()
            junta_comercial.empresa = empresa
            junta_comercial.tipo_junta = tipo
            junta_comercial.data = data
            junta_comercial.data_caderno = data_caderno
            junta_comercial.texto = texto
            if numero_alteracao:
                try:
                    junta_comercial.numero_alteracao = remove_varios_espacos(remove_caracteres_especiais(numero_alteracao.split(":")[1]))
                except IndexError:
                    junta_comercial.numero_alteracao =  remove_varios_espacos(remove_caracteres_especiais(numero_alteracao))
                except:
                    junta_comercial.numero_alteracao = 'NUMERO INVALIDO'
            self.dao.salvar(junta_comercial,commit=True, salvar_estrangeiras=False,salvar_many_to_many=False)

        if not re.search("CONSTITUICOES", tipo.nome):
            classifica_jucesp.classica_anotacao(junta_comercial,regex_util)

        return junta_comercial
        #return None
    def extrai_json_mapa(self,nome_empresa,nire):
        import requests
        s = requests.Session()
        conseguiu = False
        tentativas = 5
        cnpj = None
        while conseguiu == False or tentativas <=0:
            try:
                pagina = s.get('https://www.jucesponline.sp.gov.br/GeoJson.aspx?razao={nome_empresa}&objeto=&cnpj=&logradouro=&cep=&bairro=&municipio=&uf=SP&bempresaativa=false&filiais=true&offset=0'.format(nome_empresa=nome_empresa))
                if pagina.json():
                    conseguiu= True
            except json.decoder.JSONDecodeError as e:
                conseguiu=False
                tentativas -= 1
        for empresa in pagina.json()['featureCollection']['features']:
            if empresa['properties']['CNPJ'] == None:
                continue
            elif empresa['properties']['NIRE'] == nire:
                cnpj = empresa['properties']['CNPJ']
                enquadramento =  empresa['properties']['Enquadramento']
                endereco = empresa['properties']['Endereco']
                cep = empresa['properties']['CEP']

        return cnpj,enquadramento,endereco,cep

