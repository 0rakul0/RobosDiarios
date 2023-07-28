from pdjus.dal.GenericoDao import *
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.JuntaComercial import JuntaComercial
from pdjus.modelo.EmpresaObjetoSocial import EmpresaObjetoSocial
from pdjus.modelo.ObjetoSocial import ObjetoSocial
from pdjus.modelo.Cnae import Cnae
from pdjus.modelo.CnaeObjetoSocial import CnaeObjetoSocial
from util.StringUtil import remove_acentos,remove_varios_espacos, normaliza_tipo_empresa, iniciais_palavra,remove_tracos_pontos_barras_espacos


class EmpresaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(EmpresaDao, self).__init__(Empresa)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_cnpj(self,cnpj):
        try:
            cnpj = remove_tracos_pontos_barras_espacos(cnpj)
            return self._classe.get(self._classe._cnpj == cnpj)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nire(self,nire):
        try:
            nire = remove_tracos_pontos_barras_espacos(nire)
            return self._classe.get(self._classe.nire == nire)
        except self._classe.DoesNotExist as e:
            return None

    def get_lista_de_empresas_por_cnpj(self,cnpj):
        try:
            cnpj = remove_tracos_pontos_barras_espacos(cnpj)
            return self._classe.get(self._classe._cnpj == cnpj)
        except self._classe.DoesNotExist as e:
            return None

    def listar_ordenado_por_cnpj(self):
        try:
            return self.listar().order_by(self._classe._cnpj)
        except self._classe.DoesNotExist as e:
            return None
    def listar_cnae(self,empresa_id,fatia=1, rank=0,limit = None):
        # try:
        #     return self._classe.select().join(EmpresaObjetoSocial,on = self._classe.id == EmpresaObjetoSocial.empresa) \
        #                                                           .join(ObjetoSocial, on=ObjetoSocial.id == EmpresaObjetoSocial.objeto_social)\
        #                                                           .join(CnaeObjetoSocial,on = ObjetoSocial.id == CnaeObjetoSocial.objeto_social) \
        #                                                           .join(Cnae, on=Cnae.id == CnaeObjetoSocial.cnae).where(self._classe.id == empresa_id.id)
        # except Exception as e:
        #     print(str(e))

        schema = default_schema
        consulta = self.execute_sql(
          '''
          select c.numero from homologacao_jucesp.empresa e 
        join homologacao_jucesp.empresa_objeto_social eobj on eobj.empresa_id = e.id
        join homologacao_jucesp.objeto_social obj on obj.id = eobj.objeto_social_id 
        join homologacao_jucesp.cnae_objeto_social cnae on cnae.objeto_social_id = obj.id 
        join homologacao_jucesp.cnae c on c.id = cnae.id where e.id = '''+str(empresa_id.id))


        return consulta

    def get_no_banco_da_receita_federal_por_cnpj(self,cnpj):
        consulta = self.execute_sql(
            '''select * from public.tb_rfb_cnpj_publicos_entidades tb where tb.cnpj = '{cnpj}' '''.format(cnpj=cnpj))

        return consulta


    def get_no_banco_da_receita_federal_por_razao_social_ou_nome_fantasia(self, nome):
        consulta = self.execute_sql(f"select * from public.tb_rfb_cnpj_publicos_entidades tb where tb.razao_social = '{nome}'")
        return consulta

    def listar_empresas_da_junta_sem_cnpj(self,fatia=1, rank=0,limit = 100):
        try:
            return self.listar(fatia=fatia, rank=rank,limit=limit,random=True,distinct=True).join(JuntaComercial,on = self._classe.id == JuntaComercial.empresa).select().where(self._classe._cnpj == None)
        except Exception as e:
            print(str(e))
    def listar_cnpj_raiz(self):
        try:
            return self._classe.select().where(len(self._classe._cnpj) == 8)
        except self._classe.DoesNotExist as e:
            return None

    def listar_limite_distinto(self, start, stop):
        try:
            return self._classe.select().distinct(self._classe._nome).order_by(self._classe._nome)[start:stop]
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_cnpj(self,nome,cnpj):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            cnpj = remove_tracos_pontos_barras_espacos(cnpj)
            return self._classe.get(self._classe._cnpj == cnpj, self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None
    def get_por_nome_e_nire(self,nome,nire):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe.nire == nire, self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def filtro_reducao_nome(self, nome):
        matches_diretas = []
        matches_aprox = []

        nome = remove_varios_espacos(remove_acentos(nome)).upper()
        nome = normaliza_tipo_empresa(nome)
        iniciais = iniciais_palavra(nome)

        filtro = ''

        for inicial in iniciais:
            filtro += (inicial + '% ')

        filtro = filtro.strip()

        try:
            matches_diretas = self._classe.select().where(self._classe._nome.contains(filtro))
            filtro = filtro.replace(' ', '')
            matches_aprox = self._classe.select().where(self._classe._nome.contains(filtro))

            return matches_diretas, matches_aprox
        except self._classe.DoesNotExist as e:
            return None

if __name__ == '__main__':
    print("Contando... É mais de 9000!!!")

    count = EmpresaDao().count()

    print("Temos {} empresas. Hora do show, porra!".format(str(count)))

    i = 0

    while i < count:
        for empresa in EmpresaDao().listar_limite_distinto(i, i + 10):
            print("{}: {}".format(empresa.nome, empresa.cnpj))

        i += 10