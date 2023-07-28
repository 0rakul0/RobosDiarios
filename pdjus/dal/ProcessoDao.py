from random import randint

from peewee import fn

from pdjus.conexao.ExtensaoPeewee import neg_regexp
from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Comarca import Comarca
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.modelo.Processo import Processo, ProcessoAssunto
from pdjus.modelo.ParteProcesso import ParteProcesso
from pdjus.modelo.Movimento import Movimento
from pdjus.modelo.Parte import Parte
from pdjus.modelo.TipoParte import TipoParte
from datetime import datetime, timedelta

from pdjus.modelo.Reparticao import Reparticao
from pdjus.modelo.Tribunal import Tribunal
from pdjus.modelo.DadoExtraido import DadoExtraido
from util.StringUtil import remove_acentos,remove_varios_espacos

class ProcessoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ProcessoDao, self).__init__(Processo)

    def lista_processos_vinculados_ao_processo_principal(self, processo):
        try:
            if processo.id is None:
                return None
            else:
                return self._classe.get(self._classe.processo_principal_id== processo.id)
        except self._classe.DoesNotExist as e:
            return None

    def get_processos_filtra_tag(self, tag):
        return self._classe.select().join(DadoExtraido).join(HistoricoDado).where(HistoricoDado.marcador == tag.upper())

    def get_processo_filtra_tag_data_atualizacao(self, tag, dias, rank=0, fatia=1, limit=None, random=False, distinct=False):
        return self.listar(rank=rank, fatia=fatia, limit=limit, random=random, distinct=distinct).select().join(DadoExtraido).join(HistoricoDado)\
            .where(HistoricoDado.marcador == tag.upper(), self._classe._data_atualizacao >= (datetime.now() - timedelta(days=dias)).date())

    # def get_processos_parte_movimentos_filtra_tag_por_data(self, tag, dias, limit=None, random=False, distinct=False, rank=0, fatia=1):
    #     return self.listar(rank=rank, fatia=fatia, limit=limit, random=random, distinct=distinct).select().join(DadoExtraido)\
    #         .join(HistoricoDado).switch(self._classe).join(ParteProcesso)\
    #         .join(Parte).switch(self._classe).join(Movimento)\
    #         .switch(ParteProcesso).join(TipoParte).where((HistoricoDado.marcador == tag.upper()), (self._classe._data_atualizacao >= (datetime.now() - timedelta(days=dias))))

    def get_processos_filtra_assuntos(self, lista_assuntos): # lista classes possui os ids das classes no bd. pode melhorar fazendo busca por string...
        # return self._session.query(self._classe).join(Assunto).filter(Assunto.id.in_(lista_assuntos)).filter(
        #     self._classe.data_distribuicao == None).filter(self._classe._numero_processo.like("%2017%")).limit(
        #     100).all()

        return self._classe.select().join(Assunto).where(Assunto.id << lista_assuntos)

    # def get_processos_sem_documento(self, naoencontrados):
    #     if len(naoencontrados) > 0:
    #         return self._session.query(self._classe).outerjoin(DocumentoMovimento).filter(~self._classe._numero_processo.in_(naoencontrados)).filter(DocumentoMovimento.id == None).limit(100).all()
    #     else:
    #         return self._session.query(self._classe).outerjoin(DocumentoMovimento).filter(
    #             DocumentoMovimento.id == None).limit(100).all()

    def get_processos_nao_processados(self):
        try:
            return self._classe.select().where(self._classe.data_distribuicao == None).limit(100)
        except self._classe.DoesNotExist as e:
            return None


    def get_processos_sem_assunto(self, naoencontrados, x=1, y=0):
        #print(self._session.query(self._classe).filter(self._classe.data_distribuicao == None))
        if len(naoencontrados) > 0:
                return self._classe.select().where(self._classe.assunto == None).filter(self._classe.id % x == y).filter(self._classe._numero_processo.like("%2008%")).filter(~self._classe._numero_processo.in_(naoencontrados)).limit(100)
        else:
            return self._classe.select().where(self._classe.assunto == None).get()


    def get_por_numero_processo_sem_grau(self, numero):
        if numero.strip() == '':
            return None
        else:
            return self._classe.select().where(self._classe._numero_processo == numero).get()

    def get_por_numero_processo(self, numero,grau=1):
        try:
            if numero.strip() == '':
                return None
            else:
                return self._classe.select().where(self._classe._numero_processo == numero,self._classe.grau == grau).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_themis(self, numero):
        try:
            if numero.strip() == '':
                return None
            else:
                return self._classe.get(self._classe._numero_themis == numero)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_processo_e_tribunal(self, numero, trib,grau=1):
        try:
            if numero.strip() == '':
                return None

            return self._classe.select().join(Reparticao).join(Comarca).join(Tribunal).where(self._classe._numero_processo == numero,self._classe.grau == grau, Tribunal.id == trib.id).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processoid_fazendo_join_com_comarca(self, id):
        try:
            return self._classe.select().join(Reparticao).join(Comarca).where(self._classe.id == id).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_npu_sem_grau(self, npu):
        try:
            if npu.strip() == '' or len(npu) < 16:
                return None
            else:
                return self._classe.get(self._classe._npu == npu)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_npu(self, npu, grau=None):
        try:
            npu = Processo.formata_npu(npu)
            if npu.strip() == '' or len(npu) < 16:
                return None
            else:
                if grau:
                    return self._classe.get(self._classe._npu == npu, self._classe.grau == grau)
                else:
                    return self.get_por_npu_sem_grau(npu)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_npu_formatado_trf2(self, npu, grau=1):
        try:
            if '/' in npu:
                npu = Processo.formata_npu(npu)
                npu = npu.rjust(22, '0')
            else:
                npu = Processo.formata_npu(npu)
                npu = npu.rjust(20, '0')
            if npu.strip() == '' or len(npu) < 16:
                return None
            else:
                return self.get_por_npu(npu,grau)
        except self._classe.DoesNotExist as e:
            return None
    def get_por_numero_processo_ou_npu_e_tribunal(self, numero,grau=None, tribunal=None,is_processos_com_mesmo_npu = False):
        numero = remove_varios_espacos(
            remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))
        if is_processos_com_mesmo_npu:
            p = self.get_por_numero_processo_ou_npu(numero, grau,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)
        else:
            p = self.get_por_numero_processo_ou_npu(numero[:20],grau,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)
        if p is None:
            if tribunal is not None:
                if not grau:
                    grau = 1
                p = self.get_por_numero_processo_e_tribunal(numero,tribunal,grau)
            else:
                p = self.get_por_numero_processo(numero,grau)

        return p

    def get_por_numero_processo_ou_npu(self, numero,grau=None,is_processos_com_mesmo_npu = False):
        if numero:
            numero = remove_varios_espacos(
                remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))

            if is_processos_com_mesmo_npu:
                p = self.get_por_npu(numero, grau)
            else:
                p = self.get_por_npu(numero[:20],grau)
            if p is None:
                p = self.get_por_numero_processo(numero,grau)
            return p
        return None

    def lista_por_npus(self, *args):
        lista = []
        if len(args)>0 and type(args[0]) is list:
            args = args[0]
        for numero in args:
            if numero:
                numero = remove_varios_espacos(
                    remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))
                lista.append(numero)
        if len(lista) > 0:
            p = self._classe.select().where(self._classe._npu.in_(lista))
            return p
        return None

    def listar_por_npus_ou_numeros_processo(self, npus):
        lista = []
        processos = []

        if len(npus) == 0:
            return None

        for numero in npus:
            numero = remove_varios_espacos(remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))
            lista.append(numero)

        for npu in lista:
            p = self._classe.select().where((self._classe._npu == npu) or (self._classe._numero_processo == npu))
            if p:
                processos.append(p)

        return processos



    def lista_por_ids(self,lista, rank=0,fatia=1):
        if len(lista) > 0:
            p = self.listar(rank=rank,fatia=fatia).select().where(self._classe.id.in_(lista))
            return p
        return None

    def lista_por_numero_processo_ou_npu(self, numero):
        if numero:
            numero = remove_varios_espacos(
                remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))

            p = self._classe.select().where(self._classe._npu == numero)
            if p is None or len(p) == 0:
                p =  self._classe.select().where(self._classe._numero_processo == numero)
            return p
        return None

    def get_por_numeros(self, num1, num2):
        p = None

        if num1:
            p = self.get_por_numero_processo_ou_npu(num1)

        if num2 and not p:
            p = self.get_por_numero_processo_ou_npu(num2)

        return p

    def listar_contagem_tag_por_mes(self, tag, ano, mes, dia=None, classe_processual = None, limit=None):
        try:
            tag = self._normalizar_marcador(tag)

            neg_classe_processual = None
            if "!" in classe_processual:
                neg_classe_processual = classe_processual.split("!")[1]

                classe_processual = classe_processual.split("!")[0]

            consulta = self._classe.select() \
                .join(Distribuicao).switch(self._classe)\
                .join(DadoExtraido,on=self._classe.dado_extraido == DadoExtraido.id) \
                .join(HistoricoDado)\
                .where(HistoricoDado.marcador == tag)
            if ano and mes:
                consulta = consulta.where(Distribuicao.data_distribuicao.year == ano,Distribuicao.data_distribuicao.month == mes)

            if classe_processual:
                consulta = consulta.join(ClasseProcessual,on=Distribuicao.classe_processual == ClasseProcessual.id) \
                    .where(ClasseProcessual._nome.regexp(classe_processual))
                if neg_classe_processual:
                    consulta = consulta.where(neg_regexp(ClasseProcessual._nome, neg_classe_processual))
                if not dia:
                    consulta = consulta.select(Distribuicao.data_distribuicao.year.alias("ano"),
                                               Distribuicao.data_distribuicao.month.alias("mes"),
                                               fn.COUNT(fn.Distinct(Processo.id)).alias("count")).group_by(
                        Distribuicao.data_distribuicao.year, Distribuicao.data_distribuicao.month)
                else:
                    consulta = consulta.select(Distribuicao.data_distribuicao.year.alias("ano"),
                                               Distribuicao.data_distribuicao.month.alias("mes"),
                                               Distribuicao.data_distribuicao.day.alias("dia"),
                                               fn.COUNT(fn.Distinct(Processo.id)).alias("count")).group_by(
                        Distribuicao.data_distribuicao.year,Distribuicao.data_distribuicao.month,
                        Distribuicao.data_distribuicao.day)
                    consulta = consulta.where(Distribuicao.data_distribuicao.day == dia)
            if limit:
                consulta = consulta.having(fn.COUNT(fn.Distinct(Processo.id)) == limit)
            return consulta
        except self._classe.DoesNotExist as e:
            return None

    def listar_tag_por_mes(self, tag, ano, mes, dia=None, classe_processual = None):
        try:
            tag = self._normalizar_marcador(tag)

            neg_classe_processual = None
            if "!" in classe_processual:
                neg_classe_processual = classe_processual.split("!")[1]

                classe_processual = classe_processual.split("!")[0]

            consulta = self._classe.select() \
                .join(Distribuicao).switch(self._classe)\
                .join(DadoExtraido,on=self._classe.dado_extraido == DadoExtraido.id) \
                .join(HistoricoDado)\
                .where(HistoricoDado.marcador == tag,Distribuicao.data_distribuicao.year == ano,Distribuicao.data_distribuicao.month == mes)

            if classe_processual:
                consulta = consulta.join(ClasseProcessual,on=Distribuicao.classe_processual == ClasseProcessual.id) \
                    .where(ClasseProcessual._nome.regexp(classe_processual))
                if neg_classe_processual:
                    consulta = consulta.where(neg_regexp(ClasseProcessual._nome, neg_classe_processual))
                if dia:
                    consulta = consulta.where(Distribuicao.data_distribuicao.day == dia)
            return consulta
        except self._classe.DoesNotExist as e:
            return None

    def deletar_sorteados_a_mais(self, quantidade_a_deletar, tag, ano, mes,classe_processual):
        lista = self.listar_tag_por_mes(tag, ano, mes,  classe_processual = classe_processual)

        deletados = []
        processos = []
        i = 0
        while i < quantidade_a_deletar:
            processo =  lista[randint(0,len(lista) - 1)]
            for item in processo.dado_extraido.historicos:
                if item.marcador == tag:
                   deletados.append(item)
            if processo not in processos:
                processos.append(processo)
                i+=1

        for i in range(0,len(deletados)):
            self.excluir(deletados[i],commit=False)
        self.commit()


    def listar_por_grau(self, grau):
        try:
            return self.listar().where(self._classe.grau == grau)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal(self, trib):
        try:
            return self._classe.select().join(self._classe.reparticao).join(Comarca).\
            join(Tribunal).where(Tribunal.id == trib.id).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_classe(self, trib, classe):
        try:
            return self._classe.select().join(self._classe.classe_processual).\
                join(Reparticao).join(Comarca).\
                join(Tribunal).where( Tribunal.id == trib.id, ClasseProcessual.id == classe.id).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_classe_a_partir_de(self, trib, classe, ano, proc_princ):
        try:
            if proc_princ:

                    return self._classe.select().join(self._classe.classe_processual).\
                        join(Reparticao).join(Comarca).\
                        join(Tribunal).where( Tribunal.id == trib.id,
                                                       ClasseProcessual.id == classe.id,
                                                       Processo.data_distribuicao.year >= ano,
                                                       Processo.data_atualizacao.isnot(None),
                                                       Processo.processo_principal == None).get()
            else:

                    return self._classe.select().join(self._classe.classe_processual).\
                        join(Reparticao).join(Comarca).\
                        join(Tribunal).where( Tribunal.id == trib.id,
                                                       ClasseProcessual.id == classe.id,
                                                       Processo.data_distribuicao.year >= ano,
                                                       Processo.data_atualizacao.isnot(None)).get()
        except self._classe.DoesNotExist as e:
            return None


    def listar_por_tribunal_atualizados_partir_de(self, trib, ano, proc_princ):
        try:
            if proc_princ:

                    return self._classe.select().\
                        join(Reparticao).join(Comarca).\
                        join(Tribunal).\
                        where( Tribunal.id == trib.id,
                                                       Processo.data_distribuicao.year >= ano,
                                                       Processo.data_atualizacao.isnot(None),
                                                       Processo.processo_principal == None).get()
            else:

                    return self._classe.select().\
                        join(Reparticao).join(Comarca).\
                        join(Tribunal).\
                        where( Tribunal.id == trib.id,
                                                       Processo.data_distribuicao.year >= ano,
                                                       Processo.data_atualizacao.isnot(None)).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_limite_por_tribunal(self, trib, start, stop):
        try:
            return self._classe.select().join(Reparticao).join(Comarca).\
                join(Tribunal).where(Tribunal.id == trib.id).\
                order_by(self._classe.id).slice(start, stop).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_ano(self, trib,ano):
        try:
            return self._classe.join(Reparticao).join(Comarca).\
                join(Tribunal).get(Tribunal.id == trib.id, self._classe.data_distribuicao.year == ano).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_ate_ano(self, trib,ano):
        try:

                return self._classe.join(Reparticao).join(Comarca).\
                    join(Tribunal).get(Tribunal.id == trib.id, self._classe.data_distribuicao.year <= ano).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_apos_ano(self, trib,ano):
        try:

                return self._classe.join(Reparticao).join(Comarca).\
                    join(Tribunal).get(Tribunal.id == trib.id, self._classe.data_distribuicao.year > ano).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_processos_classe_vazia(self):
        try:

                return self._classe.get(self._classe.classe_processual_id == None)
        except self._classe.DoesNotExist as e:
            return None
    def listar_processos_data_atualizacao_vazia(self):
        try:

                return self._classe.get(self._classe.data_atualizacao == None)
        except self._classe.DoesNotExist as e:
            return None

    def listar_processos_data_atualizacao_menor_que(self, data, rank=0, fatia=1):
        try:

                return self.listar(rank=rank, fatia=fatia).select().where(self._classe.data_atualizacao < data)
        except self._classe.DoesNotExist as e:
            return None


    def listar_processos_falencia(self, rank=0, fatia=1,tag='FALENCIAS',start=None,stop=None):
        try:
            lista = list(set(self.listar(rank=rank, fatia=fatia,tag=tag,start=start,stop=stop).select().distinct().join(ProcessoAssunto,on=self._classe.id == ProcessoAssunto.processo).join(Assunto,on= ProcessoAssunto.assunto == Assunto.id)
                         .where(neg_regexp(ClasseProcessual._nome,"FALENCIA|RECUPERACAO|CONVOLACAO|CONCORDATA|CREDOR|ATOS.*MASSA|ADMINISTRACAO JUDICIAL|CONCURS.*CREDOR|DEVEDOR|FALIMENTA|FALID[OA]|((DECLARACAO|IMPUGNACAO|HABILITACAO|PREFERENCIA|CLASSIFIC).*CREDITO)|(CREDITO.*(DECLARACAO|IMPUGNACAO|HABILITACAO|PREFERENCIA|CLASSIFIC))|(INSOLVENCIA.*CIVIL)|(CIVIL.*INSOLVENCIA)"))))
            return lista
        except self._classe.DoesNotExist as e:
            return None

    def listar_processos_falencia_data_atualizacao_menor_que(self, data, rank=0, fatia=1,tag='FALENCIAS'):
        try:
            lista = list(set(self.listar(rank=rank, fatia=fatia,tag=tag).select().distinct().join(ClasseProcessual,on=self._classe.classe_processual == ClasseProcessual.id)
                         .where(self._classe.data_atualizacao < data , self._classe._data_distribuicao > '20000101',
                                (ClasseProcessual._nome.regexp("^(PEDIDO DE )?FALENCIA") |
                                 ClasseProcessual._nome.regexp("FAL.NC") |
                                 ClasseProcessual._nome.regexp("AUTOFALENCIA") |
                                 ClasseProcessual._nome.regexp("REC.*JUD") |
                                 ClasseProcessual._nome.regexp("CONCORDATA")))))
            return lista
        except self._classe.DoesNotExist as e:
            return None

    def listar_processos_atualizados_com_juiz_nulo(self,rank=0,fatia=1,limit=None,tag='FALENCIAS'):
        try:
            if tag:
                tag = self._normalizar_marcador(tag)

            return self.listar(rank=rank,fatia=fatia,limit=limit).join(DadoExtraido).join(HistoricoDado).\
                where((HistoricoDado.marcador == tag) &
                      (self._classe.data_atualizacao.is_null(False)) &
                      (self._classe.juiz.is_null(True)))

        except self._classe.DoesNotExist as e:
            return None

# if __name__ == '__main__':
#     c = ProcessoDao()
#     teste = c.get_processo_filtra_tag_data_atualizacao(tag='FALENCIAS', dias=120, distinct=False)
#     print(teste[0].partes)
#     print()