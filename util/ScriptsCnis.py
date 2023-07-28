import csv
import re

from pdjus.service.CnisEmpresaService import CnisEmpresaService
from pdjus.service.CnisEstabelecimentoService import CnisEstabelecimentoService
from pdjus.service.EstadoService import EstadoService
from pdjus.service.MunicipioService import MunicipioService


def insere_municipio():
    estado = None
    estado_service = EstadoService()
    municipio_service = MunicipioService()
    with open('C:\\Users\\b249025230\\Documents\\CNIS\\municipios.csv',encoding='utf8') as arq_csv:
        csv_processos = csv.DictReader(arq_csv, delimiter=';')
        for linha in csv_processos:
            id_muni_prev = linha['ID_MUNI_PREV']
            num_ibge = linha['NU_MUNI_IBGE']
            nome = linha['NM_MUNI']
            sigla_uf = linha['SG_UF']

            if not estado or estado.sigla != sigla_uf:
                estado = estado_service.preenche_estado(sigla_uf)

            municipio = municipio_service.preenche_municipio(nome,estado,num_ibge)

            print("{} - {} atualizado!".format(municipio.nome,municipio.estado))

#TENHO QUE INSERIR EMPRESA E ESTABELECIMENTOS
def insere_empresa_cnis():
    cnis_empresa_service = CnisEmpresaService()
    regex_linha = re.compile('(\w*?),("?.*?"?),(\w*?),(.*?),(\w*?),(\w*?),("?.*"?),(\w*?),(\d{1,2}\/\d{1,2}\/\d{2,4}),(\w+)$')
    regex_linha_duas_aspas = re.compile('(\w*?),(".*?"),(\w*?),(.*?),(\w*?),(\w*?),(".*"),(\w*?),(\d{1,2}\/\d{1,2}\/\d{2,4}),(\w+)$')
    regex_linha_primeira_aspas = re.compile('(\w*?),(".*?"),(\w*?),(.*?),(\w*?),(\w*?),(.*),(\w*?),(\d{1,2}\/\d{1,2}\/\d{2,4}),(\w+)$')
    regex_linha_segunda_aspas = re.compile('(\w*?),(.*?),(\w*?),(.*?),(\w*?),(\w*?),(".*"),(\w*?),(\d{1,2}\/\d{1,2}\/\d{2,4}),(\w+)$')

    with open('C:\\Users\\b249025230\\Documents\\CNIS\\Empresas.txt',encoding='utf8') as f:
        f.readline()
        i=0
        comeca = False
        # csv_processos = csv.DictReader(arq_csv, delimiter=';')
        for linha in f:
            i+=1
            print(linha)
            if linha.startswith('74737438,CARLOS EDUARDO CASTRO SCHULTZ'):
                comeca = True
            if comeca:
                match_linha = regex_linha_duas_aspas.search(linha)
                if not match_linha:
                    match_linha = regex_linha_primeira_aspas.search(linha)
                    if not match_linha:
                        match_linha = regex_linha_segunda_aspas.search(linha)
                        if not match_linha:
                            match_linha = regex_linha.search(linha)
                if match_linha:
                    id_empresa_estab = match_linha.group(1)
                    nome = match_linha.group(2)
                    natureza_juridica = None if match_linha.group(3) == '' else match_linha.group(3)
                    opcao_simples = match_linha.group(4)
                    situacao_prev = None if match_linha.group(5) == '' else match_linha.group(5)
                    situacao_srf = None if match_linha.group(6) == '' else match_linha.group(6)
                    nome_fantasia = match_linha.group(7)
                    microempresa = None if match_linha.group(8) == '' else match_linha.group(8)
                    data_inicio = match_linha.group(9)
                    mei = None if match_linha.group(10) == '' else match_linha.group(10)

                    cnisEmpresa = cnis_empresa_service.preenche_cnis_empresa(id_empresa_estab,nome,natureza_juridica,opcao_simples,situacao_prev,situacao_srf,nome_fantasia,microempresa,mei,data_inicio)

                    print(cnisEmpresa)

                    print('Script insere empresa - {}'.format(i))


def insere_estabelecimento():
    regex_linha = re.compile('(\w*?),(.*?),(\w*?),(.*?),(\w*?),(\w*?),(.*?),(\w*?),("?.*"?),(\d{1,2}\/\d{1,2}\/\d{2,4}),(\w*?),(\w*?),(\w*)$')
    cnis_estabelecimento_service = CnisEstabelecimentoService()
    cnis_empresa_service = CnisEmpresaService()
    with open('C:\\Users\\b249025230\\Documents\\CNIS\\Estabelecimentos.txt',encoding='utf8') as f:
        f.readline()
        i=0
        for linha in f:
            i+=1
            print(linha)
            match_linha = regex_linha.search(linha)
            if match_linha:
                id_empresa_estab = match_linha.group(1)
                id_muni_prev = None if match_linha.group(2) == '' else match_linha.group(2)
                nu_cep = None if match_linha.group(3) == '' else match_linha.group(3)
                id_uf_prev  = None if match_linha.group(4) == '' else match_linha.group(4)
                cd_situacao_prev = None if match_linha.group(5) == '' else match_linha.group(5)
                cd_situacao_srf = None if match_linha.group(6) == '' else match_linha.group(6)
                cnpj = match_linha.group(7)
                cd_matriz_filial = None if match_linha.group(8) == '' else match_linha.group(8)
                nome = match_linha.group(9)
                data_inicio_atividade = match_linha.group(10)
                cs_cnae_2_0 = None if match_linha.group(11) == '' else match_linha.group(11)
                nu_cnae_2_0 = None if match_linha.group(12) == '' else match_linha.group(12)
                nu_cnae_cmpl_2_0 = None if match_linha.group(13) == '' else match_linha.group(13)
                cnisEmpresa = cnis_empresa_service.preenche_cnis_empresa(id_empresa_estab)

                cnisEstabelecimento = cnis_estabelecimento_service.preence_cnis_estabelecimento(id_empresa_estab,cnpj, nome ,cnisEmpresa,id_muni_prev,nu_cep,id_uf_prev,cd_situacao_prev,cd_situacao_srf,cd_matriz_filial,cs_cnae_2_0,nu_cnae_2_0,nu_cnae_cmpl_2_0)

                print(cnisEstabelecimento)

                print('Script insere estabelecimento - {}'.format(i))

def corrige_nome_empresa_cnis():
    cnis_empresa_service = CnisEmpresaService()
    empresas = cnis_empresa_service.dao.listar_por_nome_com_regex_match('\(?REPR?.\s?(POR|PELA)?.*')
    for empresa in empresas:
        print('{};;;;{};;;;{}'.format(empresa.nome,empresa.nome_corrigido,empresa.nome_abreviado))
        empresa.nome = empresa.nome
        print('{};;;;{};;;;{}'.format(empresa.nome,empresa.nome_corrigido,empresa.nome_abreviado))
        cnis_empresa_service.salvar(empresa)

def corrige_nome_estabelecimento_cnis():
    cnis_estabelecimento_service = CnisEstabelecimentoService()
    estabelecimentos = cnis_estabelecimento_service.dao.listar_por_nome_com_regex_match('\(?REPR?.\s?(POR|PELA)?.*')
    for estabelecimento in estabelecimentos:
        print('{};;;;{};;;;{}'.format(estabelecimento.nome,estabelecimento.nome_corrigido,estabelecimento.nome_abreviado))
        estabelecimento.nome = estabelecimento.nome
        print('{};;;;{};;;;{}'.format(estabelecimento.nome,estabelecimento.nome_corrigido,estabelecimento.nome_abreviado))
        cnis_estabelecimento_service.salvar(estabelecimento)

