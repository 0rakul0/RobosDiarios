from util.StringUtil import remove_varios_espacos, remove_acentos,remove_links
import re
from pdjus.dal.GenericoDao import *
from pdjus.modelo.JuntaComercial import JuntaComercial
from pdjus.modelo.TipoAnotacaoJuntaComercial import TipoAnotacaoJuntaComercial
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.TipoAnotacao import TipoAnotacao


class JuntaComercialDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(JuntaComercialDao, self).__init__(JuntaComercial)


    def get_por_empresa_tipo_e_data(self,empresa,tipo,data):
        try:
            return self._classe.get(self._classe.empresa_id == empresa.id,self._classe.tipo_junta_id == tipo.id,self._classe.data == data)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_tipo_anotacao(self,tipo_anotacao,fatia=1, rank=0,limit = None):
        try:
            return self.listar(fatia=fatia, rank=rank,limit=limit).select().join(TipoAnotacaoJuntaComercial,on = self._classe.id == TipoAnotacaoJuntaComercial.junta_comercial).\
                join(TipoAnotacao,on = TipoAnotacao.id == TipoAnotacaoJuntaComercial.tipo_anotacao).join(Empresa,on = self._classe.empresa_id == Empresa.id).where(TipoAnotacao._nome == tipo_anotacao._nome,Empresa._cnpj == None)
        except Exception as e:
            print(str(e))

    def get_por_empresa_tipo_data_e_texto(self, empresa, tipo, data, texto):
        try:
            texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))

            return self._classe.get(self._classe.empresa_id == empresa.id,self._classe.tipo_junta_id == tipo.id, self._classe.data == data, self._classe._texto == texto)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_data_caderno(self,fatia=1,rank=0,limit=None,data_caderno=None):
        try:
            return self.listar(fatia=fatia, rank=rank,limit=limit).select().switch(Empresa).where(self._classe.data_caderno == data_caderno)
        except self._classe.DoesNotExist as e:
            return None

    def listar_anotacoes_nao_classificadas(self,fatia=1, rank=0,limit = None):
        try:
            #,self._classe.tipo_junta.id not in[134,131,102,108,109,110,119,136,111,124,123,127,112,113,130]
            return self.listar(fatia=fatia, rank=rank,limit=limit).select().join(TipoAnotacaoJuntaComercial,join_type=JOIN.LEFT_OUTER).where(TipoAnotacaoJuntaComercial.junta_comercial == None,self._classe._texto != '',self._classe.classificado == False,self._classe.tipo_junta.not_in([134,131,102,108,109,110,119,136,111,124,123,127,112,113,130]))
        except Exception as e:
            print(str(e))

    def listar_constituicoes(self,fatia=1, rank=0,limit = 1000):
        try:
            #,self._classe.tipo_junta.id not in[134,131,102,108,109,110,119,136,111,124,123,127,112,113,130]
            return self.listar(fatia=fatia, rank=rank,limit=limit).select().where(self._classe.classificado == False,'CONST' in self._classe.tipo_junta._nome)
        except Exception as e:
            print(str(e))

    def atualizar_view_setorial(self):
        schema = default_schema
        self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_jucesp_agregado_anotacoes; ''')
        self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_jucesp_agregado_pmc; ''')
        self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_jucesp_agregado_pms; ''')
        self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_jucesp_setores_anotacoes; ''')

    def atualiza_view_unificada(self):
        schema = default_schema
        self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_jucesp_unificado; ''')

    def get_porcentagem_anotacoes_nao_classificadas_t1(self):
        try:
            return self.execute_sql(''' select 'jucesp T1' as TIPO, x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                (select count(*),
                                date_part('year'::text, jc.data_caderno) AS ano,
                                date_part('month'::text,jc.data_caderno) AS mes
                                from homologacao_jucesp.junta_comercial jc
                                full join homologacao_jucesp.tipo_anotacao_junta_comercial tajc on tajc.junta_comercial_id = jc.id
                                full join homologacao_jucesp.tipo_anotacao ta on ta.id = tajc.tipo_anotacao_id where tajc.tipo_anotacao_id is null and jc.texto != ''
                                group by ano,mes)as x
                                join
                                -- and jc.data_caderno =
                                (select count(*),
                                date_part('year'::text, jc.data_caderno) AS ano,
                                date_part('month'::text, jc.data_caderno) AS mes
                                from homologacao_jucesp.junta_comercial jc
                                group by ano,mes)as b on x.ano=b.ano and x.mes=b.mes
                                -- where jc.data_caderno =
                                order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_objetos_nao_classificadas_t2(self):
        try:
            return self.execute_sql(''' select 'jucesp T2' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count (distinct(eos.empresa_id,eos.objeto_social_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.empresa e
                                        join homologacao_jucesp.junta_comercial jc on e.id = jc.empresa_id
                                        join homologacao_jucesp.empresa_objeto_social eos on eos.empresa_id = e.id
                                        join homologacao_jucesp.objeto_social os on os.id = eos.objeto_social_id
                                        full join homologacao_jucesp.cnae_objeto_social cos2 on cos2.objeto_social_id = os.id
                                        full join homologacao_jucesp.cnae c on c.id = cos2.cnae_id
                                        where cos2.cnae_id is null
                                        group by ano,mes)as x
                                        join
                                        (select count (distinct(eos.empresa_id,eos.objeto_social_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.empresa e
                                        join homologacao_jucesp.junta_comercial jc on e.id = jc.empresa_id
                                        join homologacao_jucesp.empresa_objeto_social eos on eos.empresa_id = e.id
                                        join homologacao_jucesp.objeto_social os on os.id = eos.objeto_social_id
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_nire_sem_cnae_t3(self):
        try:
            return self.execute_sql(''' select 'jucesp T3' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(distinct(e.id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                        where e.id not in
                                        (
                                            select distinct(jc.empresa_id) from homologacao_jucesp.junta_comercial jc
                                            join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                            join homologacao_jucesp.empresa_objeto_social eos on eos.empresa_id = e.id
                                            join homologacao_jucesp.objeto_social os on os.id = eos.objeto_social_id
                                            join homologacao_jucesp.cnae_objeto_social cos2 on cos2.objeto_social_id = os.id
                                            join homologacao_jucesp.cnae c on c.id = cos2.cnae_id
                                        )
                                        group by ano,mes)as x-- and jc.data_caderno =
                                        join
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                        group by ano,mes)as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_nire_sem_cnpj_no_mapa_t4(self):
        try:
            return self.execute_sql(''' select 'jucesp T4' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                        join homologacao_jucesp.empresa_enquadramento ee on ee.empresa_id = e.id
                                        join homologacao_jucesp.enquadramento enq on enq.id = ee.enquadramento_id where e.cnpj is null
                                        group by ano,mes) as x -- and jc.data_caderno =
                                        join
                                        (select count(distinct(jc.empresa_id)),
                                         date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                         from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_nire_sem_cnpj_fora_do_mapa_t5(self):
        try:
            return self.execute_sql(''' select 'jucesp T5' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                        where e.endereco is null and e.cep is null and e.cnpj is null
                                        group by ano,mes) as x -- where jc.data_caderno =
                                        join
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_nire_nao_encontrado_no_mapa_t6(self):
        try:
            return self.execute_sql(''' select 'jucesp T6' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id where e.endereco is null and e.cep is null
                                        group by ano, mes) as x -- and jc.data_caderno =
                                        join
                                        (select count(distinct(jc.empresa_id)),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        join homologacao_jucesp.empresa e on e.id = jc.empresa_id group by ano, mes )as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_tamanho_medio_arquivo_txt_t7(self):
        try:
            return self.execute_sql(''' select 'jucesp T7'::text AS tipo ,x.ano,x.mes, 1.0 * x.soma/b.count as tamanho_medio 
                                        from 
                                        (select sum(tamanho::DECIMAL) as soma,
                                         date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text, di.data) As mes 
                                         from homologacao_jucesp.arquivo  arq
                                        join homologacao_jucesp.diario di on arq.diario_id = di.id
                                        group by ano,mes) as x
                                        join 
                                        (select count(*) as count, 
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text, di.data) As mes
                                         from homologacao_jucesp.arquivo  arq
                                         join homologacao_jucesp.diario di on arq.diario_id = di.id
                                        group by ano,mes)as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes''')
        except Exception as e:
            print(str(e))

    def get_anotacoes_data_menor_data_caderno_t10(self):
        try:
            return self.execute_sql(''' select 'jucesp T10' as TIPO,
                                        date_part('year'::text, jc.data_caderno) AS ano_caderno,
                                        date_part('month'::text, jc.data_caderno) AS mes_caderno,
                                        count(jc.id),
                                        date_part('year'::text, jc.data) AS ano_anotacao,
                                        date_part('month'::text, jc.data) AS mes_anotacao
                                        from homologacao_jucesp.junta_comercial jc
                                        where jc.data < jc.data_caderno and jc.data >= jc.data_caderno - interval '4 month'
                                        group by date_part('month'::text, jc.data_caderno),date_part('year'::text, jc.data_caderno),date_part('month'::text, jc.data),
                                        date_part('year'::text, jc.data)
                                        order by ano_caderno, mes_caderno,ano_anotacao,mes_anotacao ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_anotacao_data_posterior_t11(self):
        try:
            return self.execute_sql(''' select 'jucesp T11' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(*),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc
                                        where jc."data" > jc.data_caderno --and jc.data_caderno = '2017_08_01'
                                        group by ano,mes) as x
                                        join
                                        (select count(*),
                                        date_part('year'::text, jc.data_caderno) AS ano,
                                        date_part('month'::text,jc.data_caderno) AS mes
                                        from homologacao_jucesp.junta_comercial jc group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_anotacao_agrupado_por_data_t12(self):
        try:
            return self.execute_sql(''' 
                                    select
                                    'jucesp T12',
                                    date_part('year'::text, jc.data_caderno) AS ano,
                                    date_part('month'::text, jc.data_caderno) AS mes,
                                    count(jc.id) as count
                                    from homologacao_jucesp.junta_comercial jc
                                    group by ano,mes
                                    order by ano,mes ''')
        except Exception as e:
            print(str(e))