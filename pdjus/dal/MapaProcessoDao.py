from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Comarca import Comarca
from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.modelo.MapaProcesso import MapaProcesso

from pdjus.modelo.Reparticao import Reparticao
from pdjus.modelo.Tribunal import Tribunal
from pdjus.modelo.DadoExtraido import DadoExtraido
from util.StringUtil import remove_acentos,remove_varios_espacos

class MapaProcessoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MapaProcessoDao, self).__init__(MapaProcesso)

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

    def get_por_npu_sem_grau(self, npu, grau=None):
        try:
            npu = MapaProcesso.formata_npu(npu)
            if npu.strip() == '' or len(npu) < 16:
                return None
            else:
                if grau:
                    return self._classe.get(self._classe._npu == npu, self._classe.grau == grau)
                else:
                    return self.get_por_npu_sem_grau(npu)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_npu(self, npu, grau=1):
        try:
            npu = MapaProcesso.formata_npu(npu)
            if npu.strip() == '' or len(npu) < 16:
                return None
            else:
                if grau:
                    return self._classe.get(self._classe._npu == npu, self._classe.grau == grau)
                else:
                    return self.get_por_npu_sem_grau(npu)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_processo(self, numero, grau=1):
        try:
            if numero.strip() == '':
                return None
            else:
                if grau:
                    return self._classe.select().where(self._classe._numero_processo == numero,self._classe.grau == grau).get()
                else:
                    return self.get_por_numero_processo_sem_grau(numero)
        except self._classe.DoesNotExist as e:
            return None

    def get_processos_sem_assunto(self, naoencontrados, x=1, y=0):
        #print(self._session.query(self._classe).filter(self._classe.data_distribuicao == None))
        if len(naoencontrados) > 0:
                return self._classe.select().where(self._classe.assunto == None).filter(self._classe.id % x == y).filter(self._classe._numero_processo.like("%2008%")).filter(~self._classe._numero_processo.in_(naoencontrados)).limit(100)
        else:
            return self._classe.select().where(self._classe.assunto == None).get()

    #
    def get_por_numero_processo_sem_grau(self, numero):
        if not numero or numero.strip() == '':
            return None
        else:
            return self._classe.select().where(self._classe._numero_processo == numero).get()

    def get_por_numero_processo_e_tribunal(self, numero, trib):
        try:
            if numero.strip() == '':
                return None

            return self._classe.select().join(Tribunal).where(self._classe._numero_processo == numero, Tribunal.id == trib.id).get()
        except self._classe.DoesNotExist as e:
            return None


    # def get_por_npu_formatado_trf2(self, npu, grau=1):
    #     try:
    #         if '/' in npu:
    #             npu = MapaProcesso.formata_npu(npu)
    #             npu = npu.rjust(22, '0')
    #         else:
    #             npu = MapaProcesso.formata_npu(npu)
    #             npu = npu.rjust(20, '0')
    #         if npu.strip() == '' or len(npu) < 16:
    #             return None
    #         else:
    #             return self.get_por_npu(npu,grau)
    #     except self._classe.DoesNotExist as e:
    #         return None
    #
    def get_por_numero_processo_ou_npu_e_tribunal(self, numero, tribunal=None):
        numero = remove_varios_espacos(
            remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))

        p = self.get_por_numero_processo_ou_npu(numero[:20])
        if p is None:
            if tribunal is not None:
                p = self.get_por_numero_processo_e_tribunal(numero,tribunal)
            else:
                p = self.get_por_numero_processo(numero)
        return p

    def get_por_numero_processo_ou_npu(self, numero,grau=None):
        if numero:
            numero = remove_varios_espacos(
                remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))

            p = self.get_por_npu(numero[:20],grau=grau)
            if p is None:
                p = self.get_por_numero_processo(numero,grau=grau)
            return p
        return None

    def get_por_numeros(self, num1, num2):
        p = None

        if num1:
            p = self.get_por_numero_processo_ou_npu(num1)

        if num2 and not p:
            p = self.get_por_numero_processo_ou_npu(num2)

        return p

    def listar_por_tribunal(self, trib):
        try:
            return self._classe.select().join(Tribunal).where(Tribunal.id == trib.id).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_classe(self, trib, classe):
        try:
            return self._classe.select().join(self._classe.classe_processual).\
                join(Tribunal).where( Tribunal.id == trib.id, ClasseProcessual.id == classe.id).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_classe_a_partir_de(self, trib, classe, ano):
        try:
            return self._classe.select().join(self._classe.classe_processual).\
                join(Reparticao).join(Comarca).\
                join(Tribunal).where( Tribunal.id == trib.id,
                                               ClasseProcessual.id == classe.id,
                                      MapaProcesso.data_distribuicao.year >= ano,
                                      MapaProcesso.data_atualizacao.isnot(None)).get()
        except self._classe.DoesNotExist as e:
            return None


    def listar_por_tribunal_atualizados_partir_de(self, trib, ano):
        try:
            return self._classe.select().\
                join(Reparticao).join(Comarca).\
                join(Tribunal).\
                where( Tribunal.id == trib.id,
                       MapaProcesso.data_distribuicao.year >= ano,
                       MapaProcesso.data_atualizacao.isnot(None)).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_limite_por_tribunal(self, trib, start, stop):
        try:
            return self._classe.select().\
                join(Tribunal).where(Tribunal.id == trib.id).\
                order_by(self._classe.id).slice(start, stop).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_por_ano(self, trib,ano):
        try:
            return self._classe.\
                join(Tribunal).get(Tribunal.id == trib.id, self._classe.data_distribuicao.year == ano).get()
        except self._classe.DoesNotExist as e:
            return None
    def listar_por_tribunal_ate_ano(self, trib,ano):
        try:

                return self._classe.\
                    join(Tribunal).get(Tribunal.id == trib.id, self._classe.data_distribuicao.year <= ano).get()
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_tribunal_apos_ano(self, trib,ano):
        try:

                return self._classe.\
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
