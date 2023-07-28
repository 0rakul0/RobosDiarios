from datetime import timedelta

from pdjus.dal.GenericoDao import *
from pdjus.modelo.Arquivo import Arquivo
from pdjus.modelo.Diario import Diario
from pdjus.modelo.StatusExtraido import StatusExtraido
import os



class ArquivoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ArquivoDao, self).__init__(Arquivo)

    def get_arquivos_nao_extraidos(self, extrator, diario,rank=0,fatia=1):
        try:
            return self._classe.select().join(Diario,JOIN.FULL).switch(self._classe).join(StatusExtraido,JOIN.FULL)\
            .where(mod(self._classe.id, fatia) == rank,Diario._nome == diario,~(
            self._classe.id <<
                (self._classe.select(self._classe.id).join(Diario).switch(self._classe).join(StatusExtraido)\
                .where(Diario._nome == diario, StatusExtraido.extrator == extrator))
            )
            ).group_by(self._classe.id, self._classe._nome_arquivo).order_by(self._classe._nome_arquivo)
        except self._classe.DoesNotExist as e:
            return None

    def get_arquivos_nao_extraido_a_partir_da_data(self,extrator, diario,data,rank=0,fatia=1):
        try:
            return self._classe.select().join(Diario,JOIN.FULL).switch(self._classe).join(StatusExtraido,JOIN.FULL)\
            .where(mod(self._classe.id, fatia) == rank,Diario._nome == diario, Diario.data >= data, ~(
            self._classe.id <<
                (self._classe.select(self._classe.id).join(Diario).switch(self._classe).join(StatusExtraido)\
                .where(Diario._nome == diario, StatusExtraido.extrator == extrator, StatusExtraido.data >= data))
            )
            ).group_by(self._classe.id, self._classe._nome_arquivo).order_by(self._classe._nome_arquivo)
        except self._classe.DoesNotExist as e:
            return None

    def get_arquivos_nao_convertidos(self, diario):
        try:
            return self._classe.select().outerjoin(self._classe.diario).where(Diario._nome == diario,
            self._classe.status_convertido == None).order_by(self._classe._nome_arquivo)
        except self._classe.DoesNotExist as e:
            return None

    def get_arquivos_por_diario(self,nome_diario):
        try:
            return self._classe.select().join(Diario).where(Diario._nome == nome_diario).order_by(
                self._classe._nome_arquivo)
        except self._classe.DoesNotExist as e:
            return None

    def get_ultima_data_baixado(self, diario):
        try:
            return self._classe.select().outerjoin(self._classe.diario).where(Diario._nome == diario,
            not self._classe.status_baixado == None).order_by(Diario.data)
        except self._classe.DoesNotExist as e:
            return None

    def _get_datas_a_baixar_sem_status(self, diario):
        try:
            return self._classe.select().outerjoin(self._classe.diario).where(Diario._nome == diario,
            self._classe.status_baixado == None).order_by(Diario.data)
        except self._classe.DoesNotExist as e:
            return None

    def get_lista_data_a_baixar(self,diario):
        lista_data = []
        atual = datetime.now().date()
        data_a_ser_baixada = self.get_ultima_data_baixado(diario)
        while data_a_ser_baixada <= atual:
            data_a_ser_baixada += timedelta(1)
            lista_data.append(data_a_ser_baixada)

        for data_a_ser_baixada in self._get_datas_a_baixar_sem_status(diario):
            lista_data.append(data_a_ser_baixada)

        return lista_data

    def get_por_nome_arquivo(self,nome_arquivo):
        try:
            return self._classe.select().where(self._classe._nome_arquivo == nome_arquivo).get()
        except self._classe.DoesNotExist as e:
            try:
                nome_arquivo = os.path.splitext(nome_arquivo)[0]
                return self._classe.select().where(self._classe._nome_arquivo == nome_arquivo).get()
            except self._classe.DoesNotExist as e:
                return None



'''
if __name__ == '__main__':
    extrator = ExtratorDao().get_por_nome('EXTRATORDJSPINDICES')
    pendentes = ArquivoDao().get_arquivos_nao_extraidos(extrator, 'DJSP').all()

    for a in pendentes:
        print(a.nome_arquivo)

    print('Total: ' + str(len(pendentes)))
'''