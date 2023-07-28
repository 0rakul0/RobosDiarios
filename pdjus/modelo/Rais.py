# -*- coding: utf-8 -*-
from pdjus.modelo.Empresa import Empresa
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_tracos_pontos_barras_espacos
from pdjus.modelo.BaseClass import *
from util.StringUtil import corrige_nome, abrevia_nome

class Rais(BaseClass):
    id = PrimaryKeyField()
    ano = TextField(null=True)
    nome_bairro = TextField(null=True)
    cei_vinculado = TextField(null=True)
    cep_estab = TextField(null=True)
    cnae_95_classe = TextField(null=True)
    cnae_20_classe = TextField(null=True)
    cnpj_centraliza_sindical = TextField(null=True)
    cnpj_contr_assist = TextField(null=True)
    cnpj_contr_assoc = TextField(null=True)
    cnpj_contr_conf = TextField(null=True)
    cnpj_contr_sindical = TextField(null=True)
    cnpj_raiz = TextField(null=True)
    data_abertura = DateField(null=True)
    data_baixa = DateField(null=True)
    data_encerramento = DateField(null=True)
    email_estabelecimento = TextField(null=True)
    ind_atividade_ano = TextField(null=True)
    ind_contrib_centralizada = TextField(null=True)
    ind_estab_participa_pat = TextField(null=True)
    ind_rais_negativa = TextField(null=True)
    ind_simples = TextField(null=True)
    ind_sindicalizacao_estab = TextField(null=True)
    natureza_juridica = TextField(null=True)
    nome_logradouro = TextField(null=True)
    numero_logradouro = TextField(null=True)
    numero_de_proprietarios = TextField(null=True)
    perc_cozinha = TextField(null=True)
    perc_alimentacao = TextField(null=True)
    perc_cesta = TextField(null=True)
    perc_refeicao = TextField(null=True)
    perc_transportadas = TextField(null=True)
    _qtd_portador_defic = FloatField(db_column='qtd_portador_defic', null=True)
    _qtd_vinculos_ativos = FloatField(db_column='qtd_vinculos_ativos', null=True)
    _qtd_vinculos_clt = FloatField(db_column='qtd_vinculos_clt', null=True)
    _qtd_vinculos_estatutarios = FloatField(db_column='qtd_vinculos_estatutarios', null=True)
    qtd_pat_5_sm = TextField(null=True)
    qtd_pat_m_5_sm = TextField(null=True)
    _razao_social = TextField(db_column='razao_social', null=True)
    cnae_20_subclasse = TextField(null=True)
    ibge_subatividade = TextField(null=True)
    ibge_subsetor = TextField(null=True)
    tamanho_estabelecimento = TextField(null=True)
    numero_telefone_contato = TextField(null=True)
    numero_telefone_empresa = TextField(null=True)
    tipo_estab = TextField(null=True)
    _vl_rem_janeiro_sc = FloatField(db_column='vl_rem_janeiro_sc', null=True)
    _vl_rem_fevereiro_sc = FloatField(db_column='vl_rem_fevereiro_sc', null=True)
    _vl_rem_marco_sc = FloatField(db_column='vl_rem_marco_sc', null=True)
    _vl_rem_abril_sc = FloatField(db_column='vl_rem_abril_sc', null=True)
    _vl_rem_maio_sc = FloatField(db_column='vl_rem_maio_sc', null=True)
    _vl_rem_junho_sc = FloatField(db_column='vl_rem_junho_sc', null=True)
    _vl_rem_julho_sc = FloatField(db_column='vl_rem_julho_sc', null=True)
    _vl_rem_agosto_sc = FloatField(db_column='vl_rem_agosto_sc', null=True)
    _vl_rem_setembro_sc = FloatField(db_column='vl_rem_setembro_sc', null=True)
    _vl_rem_outubro_sc = FloatField(db_column='vl_rem_outubro_sc', null=True)
    _vl_rem_novembro_sc = FloatField(db_column='vl_rem_novembro_sc', null=True)
    _vl_rem_dezembro_sc = FloatField(db_column='vl_rem_dezembro_sc', null=True)
    _vl_contr_assist = FloatField(db_column='vl_contr_assist', null=True)
    _vl_contr_assoc = FloatField(db_column='vl_contr_assoc', null=True)
    _vl_contr_conf = FloatField(db_column='vl_contr_conf', null=True)
    _vl_contr_sind = FloatField(db_column='vl_contr_sind', null=True)
    _cnpj__cei = TextField(db_column='cnpj__cei', null=True)
    municipio = TextField(null=True)
    _uf = TextField(db_column='uf', null=True)
    porte_estabelecimento = TextField(null=True)
    _cnpj = TextField(db_column='cnpj', null=True)
    _nome_abreviado = TextField(db_column='nome_abreviado', null=True)
    _nome_corrigido = TextField(db_column='nome_corrigido', null=True)

    # TODO: Mover esse dicionario para o modelo de Estado, esses codigos sao do IBGE
    codigosEstado = {
        '11': 'RO',
        '12': 'AC',
        '13': 'AM',
        '14': 'RR',
        '15': 'PA',
        '16': 'AP',
        '17': 'TO',
        '21': 'MA',
        '22': 'PI',
        '23': 'CE',
        '24': 'RN',
        '25': 'PB',
        '26': 'PE',
        '27': 'AL',
        '28': 'SE',
        '29': 'BA',
        '31': 'MG',
        '32': 'ES',
        '33': 'RJ',
        '35': 'SP',
        '41': 'PR',
        '42': 'SC',
        '43': 'RS',
        '50': 'MS',
        '51': 'MT',
        '52': 'GO',
        '53': 'DF'
    }

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Rais, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        return True

    def codigoEstadoUf(self, codigo):
        return self.codigosEstado[codigo]

    def testValorNumerico(self, valor):
        if valor:
            if str.isnumeric(valor.replace(',', '')):
                return float(valor.replace(',', '.'))
            else:
                return float(0)
        else:
            return float(0)

    def raisToDict(self):
        return self._data
        # return {
        #     'ano': self.ano,
        #     'nome_bairro': self.nome_bairro,
        #     'cei_vinculado': self.cei_vinculado,
        #     'cep_estab': self.cep_estab,
        #     'cnae_95_classe': self.cnae_95_classe,
        #     'cnae_20_classe': self.cnae_20_classe,
        #     'cnpj_centraliza_sindical': self.cnpj_centraliza_sindical,
        #     'cnpj_contr_assist': self.cnpj_contr_assist,
        #     'cnpj_contr_assoc': self.cnpj_contr_assoc,
        #     'cnpj_contr_conf': self.cnpj_contr_conf,
        #     'cnpj_contr_sindical': self.cnpj_contr_sindical,
        #     'cnpj_raiz': self.cnpj_raiz,
        #     'data_abertura': self.data_abertura,
        #     'data_baixa': self.data_baixa,
        #     'data_encerramento': self.data_encerramento,
        #     'email_estabelecimento': self.email_estabelecimento,
        #     'ind_atividade_ano': self.ind_atividade_ano,
        #     'ind_contrib_centralizada': self.ind_contrib_centralizada,
        #     'ind_estab_participa_pat': self.ind_estab_participa_pat,
        #     'ind_rais_negativa': self.ind_rais_negativa,
        #     'ind_simples': self.ind_simples,
        #     'ind_sindicalizacao_estab': self.ind_sindicalizacao_estab,
        #     'natureza_juridica': self.natureza_juridica,
        #     'nome_logradouro': self.nome_logradouro,
        #     'numero_logradouro': self.numero_logradouro,
        #     'numero_de_proprietarios': self.numero_de_proprietarios,
        #     'perc_cozinha': self.perc_cozinha,
        #     'perc_alimentacao': self.perc_alimentacao,
        #     'perc_cesta': self.perc_cesta,
        #     'perc_refeicao': self.perc_refeicao,
        #     'perc_transportadas': self.perc_transportadas,
        #     'qtd_portador_defic': self._qtd_portador_defic,
        #     'qtd_vinculos_ativos':self._qtd_vinculos_ativos,
        #     'qtd_vinculos_clt': self._qtd_vinculos_clt,
        #     'qtd_vinculos_estatutarios': self._qtd_vinculos_estatutarios,
        #     'qtd_pat_5_sm': self.qtd_pat_5_sm,
        #     'qtd_pat_m_5_sm': self.qtd_pat_m_5_sm,
        #     'razao_social': self._razao_social,
        #     'cnae_20_subclasse': self.cnae_20_subclasse,
        #     'ibge_subatividade': self.ibge_subatividade,
        #     'ibge_subsetor': self.ibge_subsetor,
        #     'tamanho_estabelecimento': self.tamanho_estabelecimento,
        #     'numero_telefone_contato': self.numero_telefone_contato,
        #     'numero_telefone_empresa': self.numero_telefone_empresa,
        #     'tipo_estab': self.tipo_estab,
        #     'vl_rem_janeiro_sc': self._vl_rem_janeiro_sc,
        #     'vl_rem_fevereiro_sc': self._vl_rem_fevereiro_sc,
        #     'vl_rem_marco_sc': self._vl_rem_marco_sc,
        #     'vl_rem_abril_sc': self._vl_rem_abril_sc,
        #     'vl_rem_maio_sc': self._vl_rem_maio_sc,
        #     'vl_rem_junho_sc': self._vl_rem_junho_sc,
        #     'vl_rem_julho_sc': self._vl_rem_julho_sc,
        #     'vl_rem_agosto_sc': self._vl_rem_agosto_sc,
        #     'vl_rem_setembro_sc': self._vl_rem_setembro_sc,
        #     'vl_rem_outubro_sc': self._vl_rem_outubro_sc,
        #     'vl_rem_novembro_sc': self._vl_rem_novembro_sc,
        #     'vl_rem_dezembro_sc': self._vl_rem_dezembro_sc,
        #     'vl_contr_assist': self._vl_contr_assist,
        #     'vl_contr_assoc': self._vl_contr_assoc,
        #     'vl_contr_conf': self._vl_contr_conf,
        #     'vl_contr_sind': self._vl_contr_sind,
        #     'cnpj__cei': self._cnpj__cei,
        #     'municipio': self.municipio,
        #     'uf': self._uf,
        #     'porte_estabelecimento': self.porte_estabelecimento,
        #     'cnpj': self._cnpj__cei,
        #     'nome_abreviado': self._nome_abreviado,
        #     'nome_corrigido': self._nome_corrigido
        # }

    @property
    def razao_social(self):
        if self._razao_social:
            self._razao_social = remove_varios_espacos(remove_acentos(self._razao_social.upper()))
        else:
            self._razao_social = None
        return self._razao_social

    @razao_social.setter
    def razao_social(self, value):
        if value:
            self._razao_social = remove_varios_espacos(remove_acentos(value.upper()))
        else:
            self._razao_social = None
        self.nome_corrigido = self._razao_social #assim que setar o nome, já vai corrigí-lo

    @property
    def cnpj(self):
        self._cnpj = Empresa.formata_cnpj(self._cnpj)
        return self._cnpj

    @cnpj.setter
    def cnpj(self, value):
        self._cnpj = Empresa.formata_cnpj(value)

    @property
    def cnpj__cei(self):
        self._cnpj__cei =  Empresa.formata_cnpj(self._cnpj__cei)
        return self._cnpj__cei

    @cnpj__cei.setter
    def cnpj__cei(self, value):
        self._cnpj__cei = remove_tracos_pontos_barras_espacos(value)
        self._cnpj = self._cnpj__cei

    @property
    def nome_corrigido(self):
        if self._nome_corrigido:
            self._nome_corrigido = remove_varios_espacos(remove_acentos(self._nome_corrigido.upper()))
        else:
            self._nome_corrigido = None
        return self._nome_corrigido

    @nome_corrigido.setter
    def nome_corrigido(self, value):
        if value:
            self._nome_corrigido = corrige_nome(remove_varios_espacos(remove_acentos(value.upper())))
        else:
            self._nome_corrigido = None
        self.nome_abreviado = self._nome_corrigido #assim que corrigir o nome, já vai abreviá-lo

    @property
    def nome_abreviado(self):
        if self._nome_abreviado:
            self._nome_abreviado = remove_varios_espacos(remove_acentos(self._nome_abreviado.upper()))
        else:
            self._nome_abreviado = None
        return self._nome_abreviado

    @nome_abreviado.setter
    def nome_abreviado(self, value):
        if value:
            self._nome_abreviado = abrevia_nome(remove_varios_espacos(remove_acentos(value.upper())))
        else:
            self._nome_abreviado = None
    @property
    def vl_rem_janeiro_sc(self):
        self._vl_rem_janeiro_sc = self.testValorNumerico(self._vl_rem_janeiro_sc)
        return self._vl_rem_janeiro_sc

    @vl_rem_janeiro_sc.setter
    def vl_rem_janeiro_sc(self, value):
        self._vl_rem_janeiro_sc = self.testValorNumerico(value)

    @property
    def vl_rem_fevereiro_sc(self):
        self._vl_rem_fevereiro_sc = self.testValorNumerico(self._vl_rem_fevereiro_sc)
        return self._vl_rem_fevereiro_sc

    @vl_rem_fevereiro_sc.setter
    def vl_rem_fevereiro_sc(self, value):
        self._vl_rem_fevereiro_sc = self.testValorNumerico(value)

    @property
    def vl_rem_marco_sc(self):
        self._vl_rem_marco_sc = self.testValorNumerico(self._vl_rem_marco_sc)
        return self._vl_rem_marco_sc

    @vl_rem_marco_sc.setter
    def vl_rem_marco_sc(self, value):
        self._vl_rem_marco_sc = self.testValorNumerico(value)

    @property
    def vl_rem_abril_sc(self):
        self._vl_rem_abril_sc = self.testValorNumerico(self._vl_rem_abril_sc)
        return self._vl_rem_abril_sc

    @vl_rem_abril_sc.setter
    def vl_rem_abril_sc(self, value):
        self._vl_rem_abril_sc = self.testValorNumerico(value)

    @property
    def vl_rem_maio_sc(self):
        self._vl_rem_maio_sc = self.testValorNumerico(self._vl_rem_maio_sc)
        return self._vl_rem_maio_sc

    @vl_rem_maio_sc.setter
    def vl_rem_maio_sc(self, value):
        self._vl_rem_maio_sc = self.testValorNumerico(value)

    @property
    def vl_rem_junho_sc(self):
        self._vl_rem_junho_sc = self.testValorNumerico(self._vl_rem_junho_sc)
        return self._vl_rem_junho_sc

    @vl_rem_junho_sc.setter
    def vl_rem_junho_sc(self, value):
        self._vl_rem_junho_sc = self.testValorNumerico(value)

    @property
    def vl_rem_julho_sc(self):
        self._vl_rem_julho_sc = self.testValorNumerico(self._vl_rem_julho_sc)
        return self._vl_rem_julho_sc

    @vl_rem_julho_sc.setter
    def vl_rem_julho_sc(self, value):
        self._vl_rem_julho_sc = self.testValorNumerico(value)

    @property
    def vl_rem_agosto_sc(self):
        self._vl_rem_agosto_sc = self.testValorNumerico(self._vl_rem_agosto_sc)
        return self._vl_rem_agosto_sc

    @vl_rem_agosto_sc.setter
    def vl_rem_agosto_sc(self, value):
        self._vl_rem_agosto_sc = self.testValorNumerico(value)

    @property
    def vl_rem_setembro_sc(self):
        self._vl_rem_setembro_sc = self.testValorNumerico(self._vl_rem_setembro_sc)
        return self._vl_rem_setembro_sc

    @vl_rem_setembro_sc.setter
    def vl_rem_setembro_sc(self, value):
        self._vl_rem_setembro_sc = self.testValorNumerico(value)

    @property
    def vl_rem_outubro_sc(self):
        self._vl_rem_outubro_sc = self.testValorNumerico(self._vl_rem_outubro_sc)
        return self._vl_rem_outubro_sc

    @vl_rem_outubro_sc.setter
    def vl_rem_outubro_sc(self, value):
        self._vl_rem_outubro_sc = self.testValorNumerico(value)

    @property
    def vl_rem_novembro_sc(self):
        self._vl_rem_novembro_sc = self.testValorNumerico(self._vl_rem_novembro_sc)
        return self._vl_rem_novembro_sc

    @vl_rem_novembro_sc.setter
    def vl_rem_novembro_sc(self, value):
        self._vl_rem_novembro_sc = self.testValorNumerico(value)

    @property
    def vl_rem_dezembro_sc(self):
        self._vl_rem_dezembro_sc = self.testValorNumerico(self._vl_rem_dezembro_sc)
        return self._vl_rem_dezembro_sc

    @vl_rem_dezembro_sc.setter
    def vl_rem_dezembro_sc(self, value):
        self._vl_rem_dezembro_sc = self.testValorNumerico(value)

    @property
    def vl_contr_assist(self):
        self._vl_contr_assist = self.testValorNumerico(self._vl_contr_assist)
        return self._vl_contr_assist

    @vl_contr_assist.setter
    def vl_contr_assist(self, value):
        self._vl_contr_assist = self.testValorNumerico(value)

    @property
    def vl_contr_assoc(self):
        self._vl_contr_assoc = self.testValorNumerico(self._vl_contr_assoc)
        return self._vl_contr_assoc

    @vl_contr_assoc.setter
    def vl_contr_assoc(self, value):
        self._vl_contr_assoc = self.testValorNumerico(value)

    @property
    def vl_contr_conf(self):
        self._vl_contr_conf = self.testValorNumerico(self._vl_contr_conf)
        return self._vl_contr_conf

    @vl_contr_conf.setter
    def vl_contr_conf(self, value):
        self._vl_contr_conf = self.testValorNumerico(value)

    @property
    def vl_contr_sind(self):
        self._vl_contr_sind = self.testValorNumerico(self._vl_contr_sind)
        return self._vl_contr_sind

    @vl_contr_sind.setter
    def vl_contr_sind(self, value):
        self._vl_contr_sind = self.testValorNumerico(value)

    @property
    def qtd_portador_defic(self):
        self._qtd_portador_defic = self.testValorNumerico(self._qtd_portador_defic)
        return self._qtd_portador_defic

    @qtd_portador_defic.setter
    def qtd_portador_defic(self, value):
        self._qtd_portador_defic = self.testValorNumerico(value)

    @property
    def qtd_vinculos_ativos(self):
        self._qtd_vinculos_ativos = self.testValorNumerico(self._qtd_vinculos_ativos)
        return self._qtd_vinculos_ativos

    @qtd_vinculos_ativos.setter
    def qtd_vinculos_ativos(self, value):
        self._qtd_vinculos_ativos = self.testValorNumerico(value)

    @property
    def qtd_vinculos_clt(self):
        self._qtd_vinculos_clt = self.testValorNumerico(self._qtd_vinculos_clt)
        return self._qtd_vinculos_clt

    @qtd_vinculos_clt.setter
    def qtd_vinculos_clt(self, value):
        self._qtd_vinculos_clt = self.testValorNumerico(value)

    @property
    def qtd_vinculos_estatutarios(self):
        self._qtd_vinculos_estatutarios = self.testValorNumerico(self._qtd_vinculos_estatutarios)
        return self._qtd_vinculos_estatutarios

    @qtd_vinculos_estatutarios.setter
    def qtd_vinculos_estatutarios(self, value):
        self._qtd_vinculos_estatutarios = self.testValorNumerico(value)

    @property
    def uf(self):
        self._uf = self.codigoEstadoUf(self._uf) if (str.isnumeric(self._uf)) else self._uf
        return self._uf

    @uf.setter
    def uf(self, value):
        self._uf = self.codigoEstadoUf(value) if (str.isnumeric(value)) else value
