import datetime
import re
import traceback
from _decimal import InvalidOperation, Decimal
from functools import reduce

from pdjus.modelo.BaseClass import *
from pdjus.modelo.Area import Area
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.Juiz import Juiz
from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.Reparticao import Reparticao
from pdjus.modelo.ReparticaoSegundoGrau import ReparticaoSegundoGrau
from util.StringUtil import remove_varios_espacos, remove_acentos

ProcessoAssuntoThroughDeferred = DeferredThroughModel()
class Processo(BaseClass):
    id = PrimaryKeyField(null=False)
    _numero_processo =  CharField(db_column="numero_processo")
    _npu =  CharField(db_column="npu")
    _numero_themis =  CharField(db_column="numero_themis")
    grau = IntegerField()
    justica_gratuita = CharField()
    tutela = CharField()
    numero_paginas = CharField()
    maior60 = CharField()
    observacao = TextField()
    orgao_julgador = CharField()
    relator = CharField()
    competencia_delegada = BooleanField()

    assuntos = ManyToMany(Assunto, through_model=ProcessoAssuntoThroughDeferred)

    processo_principal = ForeignKeyField("self",null=True,related_name="processos_vinculados")

    processo_primeiro_grau = ForeignKeyField("self",null=True,related_name="processos_segundo_grau")

    _data_atualizacao = DateField(db_column='data_atualizacao')
    _valor_da_acao = DecimalField(db_column='valor_da_acao')
    tipo_moeda = CharField()

    _data_distribuicao = DateTimeField(db_column = "data_distribuicao")
    _tipo_distribuicao = CharField(db_column="tipo_distribuicao")

    classe_processual = ForeignKeyField(ClasseProcessual,null=True)


    #NÃO É MAIS USADO, O CORRETO É UTILIZAR PROCESS_ASSUNTO
    #assunto = ForeignKeyField(Assunto, null=True)

    juiz = ForeignKeyField(Juiz, null=True)

    reparticao = ForeignKeyField(Reparticao,null=True)

    reparticao_segundo_grau = ForeignKeyField(ReparticaoSegundoGrau,null=True)

    area = ForeignKeyField(Area,null=True)

    dado_extraido = ForeignKeyField(DadoExtraido,null=True)

    _situacoes = []

    _partes = []

    _advogados = []

    _blocos_quadro = []

    def __init__(self,*args, **kwargs):
        self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(Processo, self).__init__(["npu","numero_processo"],*args, **kwargs)

    def is_primeiro_grau(self):
        return self.grau == 1

    def is_segundo_grau(self):
        return self.grau == 2

    @property
    def tipo_distribuicao(self):
        self._tipo_distribuicao = remove_varios_espacos(remove_acentos(self._tipo_distribuicao.strip().upper()))
        return self._tipo_distribuicao

    @tipo_distribuicao.setter
    def tipo_distribuicao(self, value):
        self._tipo_distribuicao = remove_varios_espacos(remove_acentos(value.strip().upper()))

    @property
    def valor_da_acao(self):
        return self._valor_da_acao

    @valor_da_acao.setter
    def valor_da_acao(self, value):
        if type(value) is str:
            value = Decimal(value.replace('.','').replace(',','.'))
        self._valor_da_acao = value

    @property
    def data_distribuicao(self):
        return self._data_distribuicao

    @data_distribuicao.setter
    def data_distribuicao(self, value):
        if type(value) is datetime.datetime or type(value) is datetime.date:
            self._data_distribuicao = value
        else:
            self._data_distribuicao = datetime.datetime.strptime(value, '%d/%m/%Y')

    @property
    def data_atualizacao(self):
        return self._data_atualizacao

    @data_atualizacao.setter
    def data_atualizacao(self, value):
        if type(value) is datetime.datetime:
            self._data_atualizacao = value.date()
        elif type(value) is datetime.date:
            self._data_atualizacao = value
        else:
            self._data_atualizacao = datetime.datetime.strptime(value, '%d/%m/%Y').date()


    @property
    def situacoes(self):
        self._situacoes = []
        for situacao_processo in self.situacoes_processo:
            self._situacoes.append(situacao_processo.situacao)
        return self._situacoes

    @property
    def partes(self):
        self._partes = []
        for parte_processo in self.partes_processo:
            self._partes.append(parte_processo.parte)
        return self._partes

    @property
    def advogados(self):
        self._advogados = []
        for parte_processo in self.partes_processo:
            self._advogados.extend(parte_processo.advogados)
        return self._advogados

    def blocos_quadro(self,bloco_quadro_service):
        self._blocos_quadro = bloco_quadro_service.dao.get_por_processo(self)
        #self._blocos_quadro = BlocoQuadro.select(BlocoQuadro).distinct().join(QuadroCredor).join(Processo).where(Processo.id == self.id)
        return self._blocos_quadro

    def contains_situacao(self,nome):
        for situacao in self.situacoes:
            if situacao.nome == nome.upper():
                return True
        return False

    def ultima_situacao(self):
        ultima_situacao = None
        ultima_data = None
        for situacao_processo in self.situacoes_processo:
            if not ultima_data or ultima_data > situacao_processo.data:
                ultima_data =  situacao_processo.data
                ultima_situacao = situacao_processo.situacao
        return ultima_situacao

    def is_valido(self):
        if (self.numero_processo and self.numero_processo.strip()) == "" or (self.npu and self.npu.strip() == ""):
            self.numero_processo = self.numero_processo.strip()
            self.npu = self.npu.strip()

        if not self.numero_processo and not self.npu:
            print("Nao pode existir um processo sem npu ou numero processo!")
            return False

        if not self.grau:
            print('ERRO NO PROCESSO {}'.format(self.npu_ou_num_processo))
            print("Nao pode existir um processo sem grau!")
            raise InvalidOperation("Erro:" + traceback.format_exc())

        return True



    def is_processo_falencia_recuperacao_convolacao(self):
        return (self.is_processo_da_classe_ou_assunto('falencia') or self.is_processo_da_classe_ou_assunto('autofalencia') or\
            self.is_processo_da_classe_ou_assunto('rec.*?jud') or self.is_processo_da_classe_ou_assunto('convolacao') or\
            self.is_processo_da_classe_ou_assunto('falin') or\
            self.is_processo_da_classe_ou_assunto('concordata') or self.is_processo_da_classe_ou_assunto('credor') or\
            self.is_processo_da_classe_ou_assunto('atos.*?massa') or self.is_processo_da_classe_ou_assunto('administracao judicial') or\
            self.is_processo_da_classe_ou_assunto('concurs.*?credor') or self.is_processo_da_classe_ou_assunto('devedor') or\
            self.is_processo_da_classe_ou_assunto('falimenta') or self.is_processo_da_classe_ou_assunto('falid[oa]') or\
            self.is_processo_da_classe_ou_assunto('REVOGACAO DE ATOS PRATICADOS EM PREJUIZO DE CREDORES E DA MASSA') or\
            self.is_processo_da_classe_ou_assunto('INEFICACIA DE ATOS EM RELACAO A MASSA') or\
            ((self.is_processo_da_classe_ou_assunto('declaracao') or self.is_processo_da_classe_ou_assunto('impugnacao') or\
              self.is_processo_da_classe_ou_assunto('habilitacao') or self.is_processo_da_classe_ou_assunto('preferencia') or\
             self.is_processo_da_classe_ou_assunto('classific')) and self.is_processo_da_classe_ou_assunto('credito')) or\
            (self.is_processo_da_classe_ou_assunto('insolv') and self.is_processo_da_classe_ou_assunto('civil')))



    def is_processo_da_classe_ou_assunto(self,nome):
        if len(self.assuntos) > 0 or self.classe_processual:
            if len(self.assuntos) > 0:
                for assunto in self.assuntos:
                    if re.search(nome.upper(),remove_acentos(assunto.nome.upper())):
                        return True
            if self.classe_processual:
                if re.search(nome.upper(),remove_acentos(self.classe_processual.nome.upper())):
                    return True
        return False

    @property
    def npu(self):
        if self._npu:
            self._npu = self.formata_npu(self._npu)
        return self._npu

    @classmethod
    def formata_npu(self, value):
        if '/' in value:
            value = value.rjust(22, '0')
        else:
            value = value.rjust(20, '0')
        return remove_varios_espacos(remove_acentos(value.replace(
            ' ', '').replace('/', '').replace('.', '').replace('-', '')))

    @classmethod
    def formata_npu_com_pontos(self,npu):
        try:
            if npu:
                npu = npu.rjust(20, '0')
                npu = npu[:7] + '-' + npu[7:9] + '.' + npu[9:13] + '.' + npu[13] + '.' + npu[14:16] + '.' + npu[-4:]
        except:
            pass
        return npu

    @classmethod
    def formata_numero_processo(self, value):
        return remove_varios_espacos(remove_acentos(value.replace(
            ' ', '').replace('/', '').replace('.', '').replace('-', '')))

    @npu.setter
    def npu(self, value):
        if value:
            self._npu = self.formata_npu(value)
        else:
            self._npu = None

    @property
    def numero_processo(self):
        if self._numero_processo:
            self._numero_processo = self.formata_numero_processo(self._numero_processo)
        return self._numero_processo

    @numero_processo.setter
    def numero_processo(self, value):
        if value:
            self._numero_processo = self.formata_numero_processo(value)
        else:
            self._numero_processo = None
        
    @property
    def numero_themis(self):
        if self._numero_themis:
            self._numero_themis = self.formata_npu(self._numero_themis)
        return self._numero_themis

    @numero_themis.setter
    def numero_themis(self, value):
        if value:
            self._numero_themis = self.formata_npu(value)
        else:
            self._numero_themis = None

    @property
    def npu_ou_num_processo(self):
        return self.npu or self.numero_processo or self.numero_themis

    @classmethod
    def is_npu(self,npu):
        regex_npu = re.compile('\d{7}\-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}', re.MULTILINE)
        return not regex_npu.match(npu) == None

    @classmethod
    def is_numero_processo(self,numero_processo):
        regex_n_antigo = re.compile('(\d{6,7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|'
                                         '(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|'
                                         '(\d{3}\.\d{2,4}\.\d{6}\-?\d?)|(\\b\d{15}\\b)', re.MULTILINE)

        return not regex_n_antigo.match(numero_processo) == None

    @classmethod
    def transforma_numero_processo_em_npu(self,numero_processo, jTR=None):
        if not jTR:
            jTR='826'
        if jTR == '826' and (numero_processo.startswith('583.') or numero_processo.startswith('000.')):
            numero_processo = '100'+numero_processo[3:]
        try:
            numero_processo = numero_processo.replace(' ','')
            if len(numero_processo) <= 6:
                return ""
            dados = numero_processo.replace('-','').split('.')
            if len(dados) == 3:
                ordem = "{:04d}".format(int(dados[0]))
                if len(dados[1]) == 2:
                    if int(dados[1]) > 20:
                        ano = '19'+dados[1]
                    else:
                        ano = '20'+dados[1]
                else:
                    ano = "{:04d}".format(int(dados[1]))
                numero = "{:07d}".format(int(dados[2][:-1]))
            else:
                numero_processo = numero_processo.replace('-','').replace('.','')
                ordem = '0'+numero_processo[:3]
                ano = numero_processo[5:9]
                numero = numero_processo[9:-1]
            digito = 98 - (int(numero+ano+jTR+ordem+'00') % 97)
            return "{num:07d}{digito:02d}{ano:04d}{jtr}{ordem:04d}".format(num=int(numero),digito=int(digito),ano=int(ano),jtr=jTR,ordem=int(ordem))
        except:
            return ""

class ProcessoAssunto(BaseClass):
    processo = ForeignKeyField(Processo, null=True)
    assunto = ForeignKeyField(Assunto, null=True)
    class Meta:
        primary_key = CompositeKey('processo', 'assunto')
        db_table = "processo_assunto"


ProcessoAssuntoThroughDeferred.set_model(ProcessoAssunto)