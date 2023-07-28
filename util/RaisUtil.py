# -*- coding: utf-8 -*-
import re
from datetime import datetime

from pdjus.conexao.Conexao import db
import util.StringUtil as stringUtil
from pdjus.modelo.Rais import Rais
from pdjus.service.RaisService import RaisService


class RaisUtil:

    def __init__(self):
        self._colunas_eq = {
            'cei_vinc': 'cei_vinculado',
            'cep': 'cep_estab',
            'clas_cnae_95': 'cnae_95_classe',
            'clas_cnae_20': 'cnae_20_classe',
            'clas_cnae20': 'cnae_20_classe',
            'cnpj_cen_sin': 'cnpj_centraliza_sindical',
            'cnpj_contr_central': 'cnpj_centraliza_sindical',
            'cnpj_c_assis': 'cnpj_contr_assist',
            'cnpj_c_assoc': 'cnpj_contr_assoc',
            'cnpj_c_conf': 'cnpj_contr_conf',
            'cnpj_c_sind': 'cnpj_contr_sindical',
            'radic_cnpj': 'cnpj_raiz',
            'dt_abert_or': 'data_abertura',
            'dt_baixa_or': 'data_baixa',
            'dt_encer_or': 'data_encerramento',
            'email': 'email_estabelecimento',
            'ind_ativ_ano': 'ind_atividade_ano',
            'ind_atividade': 'ind_atividade_ano',
            'ind_centr': 'ind_contrib_centralizada',
            'ind_contr_central': 'ind_contrib_centralizada',
            'ind_pat': 'ind_estab_participa_pat',
            'ind_rais_neg': 'ind_rais_negativa',
            'ind_simples': 'ind_simples',
            'ind_sind_est': 'ind_sindicalizacao_estab',
            'nat_juridica': 'natureza_juridica',
            'natur_jur': 'natureza_juridica',
            'endereco': 'nome_logradouro',
            'logradouro': 'nome_logradouro',
            'perc_pat_coz': 'perc_cozinha',
            'perc_pat_ali': 'perc_alimentacao',
            'perc_pat_ces': 'perc_cesta',
            'perc_pat_ref': 'perc_refeicao',
            'perc_pat_tra': 'perc_transportadas',
            'qt_port_defi': 'qtd_portador_defic',
            'estoque': 'qtd_vinculos_ativos',
            'est_clt_out': 'qtd_vinculos_clt',
            'estoque_esta': 'qtd_vinculos_estatutarios',
            'qt_pat5sm': 'qtd_pat_5_sm',
            'qt_patm5sm': 'qtd_pat_m_5_sm',
            'qt_vinc_pat_ate_5sm': 'qtd_pat_5_sm',
            'qt_vinc_pat_sup_5sm': 'qtd_pat_m_5_sm',
            'razao_social': 'razao_social',
            'sb_clas_20': 'cnae_20_subclasse',
            'subativ_ibge': 'ibge_subatividade',
            'subs_ibge': 'ibge_subsetor',
            'tamestab': 'tamanho_estabelecimento',
            'telef_cont': 'numero_telefone_contato',
            'telefone_contato': 'numero_telefone_contato',
            'telef_empr': 'numero_telefone_empresa',
            'telefone_estab': 'numero_telefone_empresa',
            'tel_contato': 'numero_telefone_contato',
            'tel_empresa': 'numero_telefone_empresa',
            'tipo_estbl': 'tipo_estab',
            'janeiro': 'vl_rem_janeiro_sc',
            'fevereiro': 'vl_rem_fevereiro_sc',
            'marco': 'vl_rem_marco_sc',
            'abril': 'vl_rem_abril_sc',
            'maio': 'vl_rem_maio_sc',
            'junho': 'vl_rem_junho_sc',
            'julho': 'vl_rem_julho_sc',
            'agosto': 'vl_rem_agosto_sc',
            'setembro': 'vl_rem_setembro_sc',
            'outubro': 'vl_rem_outubro_sc',
            'novembro': 'vl_rem_novembro_sc',
            'dezembro': 'vl_rem_dezembro_sc',
            'vl_con_assis': 'vl_contr_assist',
            'vl_con_assoc': 'vl_contr_assoc',
            'vl_con_conf': 'vl_contr_conf',
            'vl_con_sind': 'vl_contr_sind',
            'identificad': 'cnpj__cei',
            'municipio': 'municipio',
            'uf': 'uf',
            'porte_estab': 'porte_estabelecimento',
            'nome_bairro': 'nome_bairro',
            'bairro': 'nome_bairro',
            'cei_vinculado': 'cei_vinculado',
            'cep_estab': 'cep_estab',
            'cnae_95_classe': 'cnae_95_classe',
            'cnae_20_classe': 'cnae_20_classe',
            'cnpj_centraliza_sindical': 'cnpj_centraliza_sindical',
            'cnpj_contr_assist': 'cnpj_contr_assist',
            'cnpj_contr_assoc': 'cnpj_contr_assoc',
            'cnpj_contr_conf': 'cnpj_contr_conf',
            'cnpj_contr_sindical': 'cnpj_contr_sindical',
            'cnpj_contr_sind': 'cnpj_contr_sindical',
            'cnpj_raiz': 'cnpj_raiz',
            'data_abertura': 'data_abertura',
            'data_baixa': 'data_baixa',
            'data_encerramento': 'data_encerramento',
            'email_estabelecimento': 'email_estabelecimento',
            'ind_atividade_ano': 'ind_atividade_ano',
            'ind_contrib_centralizada': 'ind_contrib_centralizada',
            'ind_estab_participa_pat': 'ind_estab_participa_pat',
            'ind_rais_negativa': 'ind_rais_negativa',
            'ind_simples': 'ind_simples',
            'ind_sindicalizacao_estab': 'ind_sindicalizacao_estab',
            'ind_estab_sind': 'ind_sindicalizacao_estab',
            'natureza_juridica': 'natureza_juridica',
            'nome_logradouro': 'nome_logradouro',
            'numero_logradouro': 'numero_logradouro',
            'numero_de_proprietarios': 'numero_de_proprietarios',
            'nu_proprietarios': 'numero_de_proprietarios',
            'perc_cozinha': 'perc_cozinha',
            'perc_alimentacao': 'perc_alimentacao',
            'perc_cesta': 'perc_cesta',
            'perc_refeicao': 'perc_refeicao',
            'perc_transportadas': 'perc_transportadas',
            'qtd_portador_defic': 'qtd_portador_defic',
            'qt_port_defic': 'qtd_portador_defic',
            'qtd_vinculos_ativos': 'qtd_vinculos_ativos',
            'qt_vinc_ativos': 'qtd_vinculos_ativos',
            'qtd_vinculos_clt': 'qtd_vinculos_clt',
            'qt_vinc_clt': 'qtd_vinculos_clt',
            'qtd_vinculos_estatutarios': 'qtd_vinculos_estatutarios',
            'qt_vinc_estat': 'qtd_vinculos_estatutarios',
            'qtd_pat_5_sm': 'qtd_pat_5_sm',
            'qtd_pat_m_5_sm': 'qtd_pat_m_5_sm',
            'razao_social': 'razao_social',
            'cnae_20_subclasse': 'cnae_20_subclasse',
            'ibge_subatividade': 'ibge_subatividade',
            'ibge_subsetor': 'ibge_subsetor',
            'tamanho_estabelecimento': 'tamanho_estabelecimento',
            'numero_telefone_contato': 'numero_telefone_contato',
            'numero_telefone_empresa': 'numero_telefone_empresa',
            'tipo_estab': 'tipo_estab',
            'vl_rem_janeiro_sc': 'vl_rem_janeiro_sc',
            'vl_rem_fevereiro_sc': 'vl_rem_fevereiro_sc',
            'vl_rem_marco_sc': 'vl_rem_marco_sc',
            'vl_rem_abril_sc': 'vl_rem_abril_sc',
            'vl_rem_maio_sc': 'vl_rem_maio_sc',
            'vl_rem_junho_sc': 'vl_rem_junho_sc',
            'vl_rem_julho_sc': 'vl_rem_julho_sc',
            'vl_rem_agosto_sc': 'vl_rem_agosto_sc',
            'vl_rem_setembro_sc': 'vl_rem_setembro_sc',
            'vl_rem_outubro_sc': 'vl_rem_outubro_sc',
            'vl_rem_novembro_sc': 'vl_rem_novembro_sc',
            'vl_rem_dezembro_sc': 'vl_rem_dezembro_sc',
            'vl_rem_estab_01': 'vl_rem_janeiro_sc',
            'vl_rem_estab_02': 'vl_rem_fevereiro_sc',
            'vl_rem_estab_03': 'vl_rem_marco_sc',
            'vl_rem_estab_04': 'vl_rem_abril_sc',
            'vl_rem_estab_05': 'vl_rem_maio_sc',
            'vl_rem_estab_06': 'vl_rem_junho_sc',
            'vl_rem_estab_07': 'vl_rem_julho_sc',
            'vl_rem_estab_08': 'vl_rem_agosto_sc',
            'vl_rem_estab_09': 'vl_rem_setembro_sc',
            'vl_rem_estab_10': 'vl_rem_outubro_sc',
            'vl_rem_estab_11': 'vl_rem_novembro_sc',
            'vl_rem_estab_12': 'vl_rem_dezembro_sc',
            'vl_contr_assist': 'vl_contr_assist',
            'vl_contr_assoc': 'vl_contr_assoc',
            'vl_contr_conf': 'vl_contr_conf',
            'vl_contr_sind': 'vl_contr_sind',
            'cnpj__cei': 'cnpj__cei',
            'municipio': 'municipio',
            'uf': 'uf',
            'porte_estabelecimento': 'porte_estabelecimento',
            'tipo_estb_id': 'tipo_estab',
            'nat_jurid': 'natureza_juridica',
            'nat_jur2016': 'natureza_juridica',
            'ind_cei_vinc': 'ind_cei_vinc',
            'regiao_metro': 'rg_metro',
            'rg_metro': 'rg_metro'
        }
        self._colunas_privadas = [
            'vl_rem_janeiro_sc',
            'vl_rem_fevereiro_sc',
            'vl_rem_marco_sc',
            'vl_rem_abril_sc',
            'vl_rem_maio_sc',
            'vl_rem_junho_sc',
            'vl_rem_julho_sc',
            'vl_rem_agosto_sc',
            'vl_rem_setembro_sc',
            'vl_rem_outubro_sc',
            'vl_rem_novembro_sc',
            'vl_rem_dezembro_sc',
            'vl_contr_assist',
            'vl_contr_assoc',
            'vl_contr_conf',
            'vl_contr_sind',
            'cnpj__cei',
            'uf',
            'cnpj',
            'nome_abreviado',
            'nome_corrigido',
            'qtd_portador_defic',
            'qtd_vinculos_ativos',
            'qtd_vinculos_clt',
            'qtd_vinculos_estatutarios',
            'razao_social',
            'data_abertura',
            'data_baixa',
            'data_encerramento'
        ]


    def formatar_coluna(self, texto):
        return stringUtil.remove_acentos(texto
                                         .replace('\t', ';')
                                         .replace('.', '')
                                         .replace('/', '')
                                         .replace('(', '')
                                         .replace(')', '')
                                         .replace('__', '_')
                                         .replace('-', '_')
                                         .replace(' ', '_')
                                         .replace('\n', '')
                                         .replace('"', '')
                                         .lower()
                                         )

    def corrige_colunas(self, colunas_antigas):
        colunas_corrigidas = []
        for coluna in colunas_antigas:
            try:
                if self._colunas_eq[coluna]:
                    colunas_corrigidas.append(self._colunas_eq[coluna])
                else:
                    colunas_corrigidas.append(coluna)
            except KeyError as e:
                colunas_corrigidas.append(coluna)
                print("coluna não existe " + str(coluna))
        return colunas_corrigidas

    def acertar_data(self, data):
        if None:
            return '0'
        if len(data) == 7:
            return '0' + data
        if len(data) == 4:
            return '0' + data[0:1] + '0' + data[2:3]
        if data == '00000000':
            return '0'
        if data == '00000000000000':
            return '0'
        if data == '00000000':
            return '0'
        return data

    def corrige_texto(self, coluna, valor):
        if coluna not in self._colunas_privadas:
            return stringUtil.remove_varios_espacos(stringUtil.remove_acentos(valor))
        else:
            return valor

    def insere_dados(self, url, arquivo):
        rais_service = RaisService()

        ano = re.search("(\d{4})",arquivo).group(1)
        with open(url, mode='r') as file:
            linha = file.readline()
            campos_com_virgula = re.findall(',("(.*?)(,)(.*?)")',linha)
            for campo in campos_com_virgula:
                linha_resultado = campo.group(0).replace(",","#")
                linha = linha.replace(campo.group(0),linha_resultado)
            linha = linha.replace(",",";")
            linha = linha.replace("#", ",")
            columns = self.corrige_colunas(self.formatar_coluna(linha).split(';'))
            index = 0
            count = 0
            for line in file:
                if count >= 3351649:

                    linha = line
                    campos_com_virgula = re.findall(',("(.*?)(,)(.*?)")', linha)
                    for campo in campos_com_virgula:
                        linha_resultado = campo[0].replace(",", "#")
                        linha = linha.replace(campo[0], linha_resultado)
                    linha = linha.replace(",", ";")
                    linha = linha.replace("#", ",")
                    line = linha

                    values = line.split(';')
                    raisObj = Rais()
                    # insere linha somente se os dados estiverem corretos
                    if len(columns) == len(values):
                        for i in range(0, len(columns)):
                            if columns[i] == 'data_abertura' or columns[i] == 'data_baixa' or columns[i] == 'data_encerramento':
                                values[i] = self.acertar_data(values[i])
                                try:
                                    values[i] = datetime.strptime(values[i], '%d%m%Y').date() if len(
                                        values[i]) > 6 else None
                                except:
                                    values[i] = None
                            if columns[i] != 'ind_cei_vinc' and columns[i] != 'rg_metro':
                                setattr(raisObj, columns[i], self.corrige_texto(columns[i], values[i]))
                            raisObj.ano = ano

                        rais_service.salvar(raisObj,commit=False)
                        index += 1
                count += 1
                print('linha ' + str(count))

                if index >= 150:
                    index = 0
                    rais_service.dao.commit()

if __name__ == "__main__":
    arquivos = [
        'estab_2017.csv'
    ]
    raisUtil = RaisUtil()
    for arquivo in arquivos:
        rais_url = 'C:\\Users\\b120558711\\Documents\\rais 2017\\' + arquivo
        raisUtil.insere_dados(rais_url, arquivo)
