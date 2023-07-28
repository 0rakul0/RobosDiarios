from pdjus.modelo.Caderno import Caderno
from pdjus.modelo.DistribuicaoAssunto import DistribuicaoAssunto
from pdjus.modelo.ParteDistribuicao import ParteDistribuicao
from pdjus.modelo.ParteDistribuicao import ParteDistribuicaoRais
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Diario import Diario
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Assunto import Assunto
from pdjus.dal.GenericoDao import *
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.TipoParte import TipoParte


class DistribuicaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(DistribuicaoDao, self).__init__(Distribuicao)



    def listar_pessoa_juridica_tag_por_mes(self, tag, ano, mes,dia=None, classe_processual=None,tipo_parte = None,limit=100,proporcao = 0.5,completa=False,limita=True):
        if not proporcao:
            proporcao=0.5
        if proporcao > 1.0 and proporcao <= 0.0:
            raise IndexError("Proporção é um percentual de 0.1 à 1.0")
        complementar = abs(proporcao - 1) * float(limit)
        limit = limit * proporcao

        if not completa:
            consulta = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual,  limit=limit)
            consulta_complementar = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual, limit=complementar)
        else:
            consulta = self.listar_data_contagem_tag(tag,classe_processual=classe_processual, limit= limit,ano=ano,mes=mes,limita=limita)
            consulta_complementar = self.listar_data_contagem_tag(tag, classe_processual=classe_processual, limit= complementar,ano=ano,mes=mes,limita=limita)

        lista = (self.listar_por_parte_distribuicao(consulta, tipo_parte,pessoa_juridica=True,banco = False))
        if complementar > 0:
            lista= lista | (self.listar_por_parte_distribuicao(consulta_complementar, tipo_parte,pessoa_juridica=False))

        return lista

    def listar_por_parte_distribuicao(self, consulta_por_mes, tipo_parte=None,pessoa_juridica=None,banco=None,pequena_empresa=None,setor = None):

        if tipo_parte:
            consulta_por_mes =  consulta_por_mes.join(ParteDistribuicao,on=(ParteDistribuicao.distribuicao == self._classe.id)).join(TipoParte).where(TipoParte._nome.regexp(tipo_parte))
        else:
            consulta_por_mes = consulta_por_mes.join(ParteDistribuicao,on=(ParteDistribuicao.distribuicao == self._classe.id))

        if pessoa_juridica is not None:
            consulta_por_mes = consulta_por_mes.where(ParteDistribuicao.pessoa_juridica == pessoa_juridica)
        if banco is not None:
            consulta_por_mes = consulta_por_mes.where(ParteDistribuicao.banco == banco)
        if pequena_empresa is not None:
            consulta_por_mes = consulta_por_mes.where(ParteDistribuicao.pequena_empresa == pequena_empresa)
        if setor is not None:
            consulta_por_mes = consulta_por_mes.where(ParteDistribuicao.pessoa_juridica == True,ParteDistribuicao.setor == setor)

        return  consulta_por_mes


    def listar_banco_tag_por_mes(self, tag, ano, mes,dia=None, classe_processual=None,tipo_parte=None, limit=100,proporcao = 0.5,completa=False,limita=True):
        if not proporcao:
            proporcao=0.5
        if proporcao > 1.0 and proporcao <= 0.0:
            raise IndexError("Proporção é um percentual de 0.1 à 1.0")
        complementar = abs(proporcao - 1) * float(limit)
        limit = limit * proporcao

        if not completa:
            consulta_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual, limit= limit)
            consulta_complementar_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual, limit= complementar)
        else:
            consulta_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual, limit= limit,ano=ano,mes=mes,limita=limita)
            consulta_complementar_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual, limit= complementar,ano=ano,mes=mes,limita=limita)

        lista = (self.listar_por_parte_distribuicao(consulta_por_mes, tipo_parte, banco=True))
        if complementar > 0:
            lista= lista | (self.listar_por_parte_distribuicao(consulta_complementar_por_mes, tipo_parte, pessoa_juridica=True,banco=False))

        return lista

    def listar_pequena_empresa_tag_por_mes(self, tag, ano, mes,dia=None, classe_processual=None, tipo_parte = None, limit=100, proporcao=0.5,completa=False,limita=True):
        if not proporcao:
            proporcao=0.5
        if proporcao > 1.0 and proporcao <= 0.0:
            raise IndexError("Proporção é um percentual de 0.1 à 1.0")
        complementar = abs(proporcao - 1) * float(limit)
        limit = limit * proporcao

        if not completa:
            consulta_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual, limit= limit)
            consulta_complementar_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia, classe_processual=classe_processual, limit= complementar)
        else:
            consulta_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual, limit= limit,limita=limita)
            consulta_complementar_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual,limit= complementar,limita=limita)
        lista = (self.listar_por_parte_distribuicao(consulta_por_mes, tipo_parte, pequena_empresa=True))
        if complementar > 0:
            lista= lista | (self.listar_por_parte_distribuicao(consulta_complementar_por_mes, tipo_parte, pessoa_juridica=True,pequena_empresa=False))

        return lista

    def listar_setor_tag_por_mes(self, tag, ano, mes,dia=None, classe_processual=None, tipo_parte = None,limit=100, proporcao=1.0,completa=False,setor=None,limita=True):
        if not proporcao:
            proporcao=1.0
        if proporcao > 1.0 and proporcao <= 0.0:
            raise IndexError("Proporção é um percentual de 0.1 à 1.0")
        complementar = abs(proporcao - 1) * float(limit)
        limit = limit * proporcao

        if not completa:
            consulta_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia,classe_processual= classe_processual, limit=limit)
            #consulta_complementar_por_mes = self.listar_tag_por_mes(tag, ano, mes,dia,classe_processual= classe_processual,limit= complementar)
        else:
            consulta_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual, limit= limit,ano=ano,mes=mes,limita=limita)
            #consulta_complementar_por_mes = self.listar_data_contagem_tag(tag, classe_processual=classe_processual,limit=complementar,ano=ano,mes=mes)
        lista = (self.listar_por_parte_distribuicao(consulta_por_mes, tipo_parte,setor=setor))
        #if complementar > 0:
        #    lista= lista | (self.listar_por_parte_distribuicao(consulta_complementar_por_mes, tipo_parte,setor=setor))

        return lista


    def listar_tag_por_mes(self, tag, ano, mes,dia=None,tag_destino=None,classe_processual = None,limit = None):
        try:
            tag = self._normalizar_marcador(tag)

            neg_classe_processual = None
            if classe_processual and "!" in classe_processual:
                neg_classe_processual = classe_processual.split("!")[1]

                classe_processual = classe_processual.split("!")[0]

            consulta = self._classe.select().join(DadoExtraido) \
                .join(HistoricoDado).switch(self._classe) \
                .where \
                    (
                    HistoricoDado.marcador == tag
                )
            if tag_destino:
                tag_destino = self._normalizar_marcador(tag_destino)
                subquery = DadoExtraido.select('1').join(HistoricoDado).where(DadoExtraido.id == self._classe.dado_extraido_id,HistoricoDado.marcador == tag_destino)
                consulta = consulta.select().where(self.not_exists(subquery))
            if dia:
                consulta = consulta.select().join(Caderno).join(Diario).switch(self._classe).where(Diario.data.year == ano,Diario.data.month == mes,Diario.data.day == dia)
            else:
                consulta = consulta.select().where(self._classe.data_distribuicao.year == ano,self._classe.data_distribuicao.month == mes)

            if classe_processual:
                consulta = consulta.select().join(ClasseProcessual) \
                    .where(ClasseProcessual._nome.regexp(classe_processual))
                if neg_classe_processual:
                    consulta = consulta.select().where(neg_regexp(ClasseProcessual._nome,neg_classe_processual))


            consulta = consulta.order_by(fn.Random())

            if limit:
                consulta = consulta.limit(limit)
            return consulta
        except self._classe.DoesNotExist as e:
            return None

    def listar_data_contagem_tag(self, tag, classe_processual=None, limit=100, mensal = True,ano=None,mes=None,limita= True):
        try:
            tag = self._normalizar_marcador(tag)

            neg_classe_processual = None
            if "!" in classe_processual:
                neg_classe_processual = classe_processual.split("!")[1]

                classe_processual = classe_processual.split("!")[0]

            consulta = self._classe.select(self._classe.data_distribuicao.year,self._classe.data_distribuicao.month,fn.COUNT(fn.Distinct(Processo.id)))\
                .join(Processo,on = self._classe.processo == Processo.id).join(DadoExtraido,on=Processo.dado_extraido == DadoExtraido.id) \
                .join(HistoricoDado).switch(self._classe) \
                .where(HistoricoDado.marcador == tag)

            if classe_processual:
                consulta = consulta.join(ClasseProcessual) \
                    .where(ClasseProcessual._nome.regexp(classe_processual))
                if neg_classe_processual:
                    consulta = consulta.where(neg_regexp(ClasseProcessual._nome, neg_classe_processual))
                if mensal:
                    consulta = consulta.select(self._classe.data_distribuicao.year.alias("ano"),
                                               self._classe.data_distribuicao.month.alias("mes"),
                                               fn.COUNT(fn.Distinct(Processo.id)).alias("count")).group_by(
                        self._classe.data_distribuicao.year, self._classe.data_distribuicao.month)
                    if limita:
                        consulta = consulta.having(fn.COUNT(fn.Distinct(Processo.id)) < limit)
                else:
                    consulta = consulta.select(self._classe.data_distribuicao.year.alias("ano"),
                                               self._classe.data_distribuicao.month.alias("mes"),
                                               self._classe.data_distribuicao.day.alias("dia"),
                                               fn.COUNT(fn.Distinct(Processo.id)).alias("count")).group_by(
                        self._classe.data_distribuicao.year, self._classe.data_distribuicao.month, self._classe.data_distribuicao.day)
                    if limita:
                        consulta = consulta.having(fn.COUNT(fn.Distinct(Processo.id)) < limit)
            if ano and mensal:
                consulta = consulta.where(self._classe.data_distribuicao.year == ano,
                    self._classe.data_distribuicao.month == mes)

            return consulta.order_by(fn.Random())

        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_processo(self,numero):
        try:
            if numero and numero.strip() == '':
                return None
            numero = Distribuicao.formata_numero_processo(numero)
            return self._classe.select().where(self._classe._numero_processo == numero)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_lista_de_numero_processo(self,rank=0,fatia=1,limit=None,lista_numero_processo=[]):
        try:
            return self.listar(rank=rank, fatia=fatia, limit=limit).select().\
                where((self._classe._numero_processo << lista_numero_processo))
        except self._classe.DoesNotExist as e:
            return None

    def get_distribuicao_com_rais_por_numero_processo(self,numero):
        try:
            if numero and numero.strip() == '':
                return None
            numero = Distribuicao.formata_numero_processo(numero)
            return self._classe.select().join(ParteDistribuicao).join(ParteDistribuicaoRais).where(self._classe._numero_processo == numero).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_distribuicao_com_rais(self):
        try:
            return self._classe.select().join(ParteDistribuicao).join(ParteDistribuicaoRais)
        except self._classe.DoesNotExist as e:
            return None


    def get_por_numero_processo_caderno(self,numero,caderno):
        try:
            if numero and numero.strip() == '':
                return None
            numero = Distribuicao.formata_numero_processo(numero)
            return self._classe.select().where(self._classe._numero_processo == numero,self._classe.caderno == caderno)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_processo_comarca_classe_processual_partes(self, numero, comarca, classe_processual, partes, cache=False):
        try:
            if numero and numero.strip() == '':
                return None

            nomes_partes = [partes]
            if cache:
                partes_str = "".join(nomes_partes)
                key = numero+str(comarca)+str(classe_processual)+str(partes_str)
                obj = self.get_cached_object(key)
                if not obj:
                    obj = self._classe.select().join(ParteDistribuicao).where(self._classe._numero_processo == numero,self._classe.comarca == comarca,self._classe.classe_processual == classe_processual,ParteDistribuicao.parte << nomes_partes).get()
                    if obj:
                        self.add_to_cache(obj)
                return obj
            else:
                return self._classe.select().join(ParteDistribuicao).where(self._classe._numero_processo == numero,self._classe.comarca == comarca,self._classe.classe_processual == classe_processual,ParteDistribuicao.parte << nomes_partes).get()

        except self._classe.DoesNotExist as e:
            return None

    def get_quantidade_por_classe_ano_mes(self,classe_processual,ano,mes):
        try:
            obj = self._classe.select().join(ClasseProcessual).where(self._classe.data_distribuicao.year == ano,self._classe.data_distribuicao.month == mes,ClasseProcessual._nome.regexp(classe_processual))
            return obj.count()
        except self._classe.DoesNotExist as e:
            return None

    def get_quantidade_pj_por_tipo_parte_classe_ano_mes(self,tipo_parte,classe_processual,ano,mes):
        try:
            obj = self._classe.select().join(ClasseProcessual).switch().join(ParteDistribuicao).join(TipoParte).where(TipoParte._nome.regexp(tipo_parte),ParteDistribuicao.pessoa_juridica == True,self._classe.data_distribuicao.year == ano,self._classe.data_distribuicao.month == mes,ClasseProcessual._nome.regexp(classe_processual))
            return obj.count()
        except self._classe.DoesNotExist as e:
            return None

    def get_quantidade_banco_por_tipo_parte_classe_ano_mes(self,tipo_parte,classe_processual,ano,mes):
        try:
            obj = self._classe.select().join(ClasseProcessual).switch().join(ParteDistribuicao).join(TipoParte).where(TipoParte._nome.regexp(tipo_parte),ParteDistribuicao.banco == True,self._classe.data_distribuicao.year == ano,self._classe.data_distribuicao.month == mes,ClasseProcessual._nome.regexp(classe_processual))
            return obj.count()
        except self._classe.DoesNotExist as e:
            return None

    def get_quantidade_setor_por_tipo_parte_classe_ano_mes(self,tipo_parte,classe_processual,ano,mes):
        try:
            obj = self._classe.select().join(ClasseProcessual).switch().join(ParteDistribuicao).join(TipoParte).where(TipoParte._nome.regexp(tipo_parte),ParteDistribuicao.setor == "serviços",self._classe.data_distribuicao.year == ano,self._classe.data_distribuicao.month == mes,ClasseProcessual._nome.regexp(classe_processual))
            return obj.count()
        except self._classe.DoesNotExist as e:
            return None


    def atualiza_indice_contagem(self):
        schema = default_schema
        indice = self.execute_sql(''' REFRESH MATERIALIZED VIEW '''+schema+'''.indice_contagem_unificado; ''')
        indice = self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_mensal_agregado_data_old; ''')
        indice = self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_mensal_pj_pf_data_old; ''')
        indice = self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_mensal_pjfin_pjnfin_data_old; ''')
        indice = self.execute_sql(''' REFRESH MATERIALIZED VIEW ''' + schema + '''.indice_mensal_setor_data_old; ''')

    def atualiza_indice_mensal(self):
        schema = default_schema
        # indice = self.execute_sql('''
        # REFRESH MATERIALIZED VIEW '''+schema+'''.indice_mensal_agrupado_agregado;
        # REFRESH MATERIALIZED VIEW '''+schema+'''.indice_mensal_agrupado_pj_pf;
        # REFRESH MATERIALIZED VIEW '''+schema+'''.indice_mensal_agrupado_pjfin_pjnfin;
        # REFRESH MATERIALIZED VIEW '''+schema+'''.indice_mensal_agrupado_setor;
        # ''')

    def get_indice_jucesp(self):
        schema = 'homologacao_jucesp'
        indice = self.execute_sql(
                    '''
                    (
                    (SELECT tipo, anotacao as classe, ano, mes, contagem FROM ''' + schema + '''.indice_jucesp_unificado)
                     )
                     order by tipo, classe, ano, mes
                     ''')

        return indice

    def get_indice_contagem(self,autor,reu):
        schema = default_schema
        indice = self.execute_sql((
             '''
             (
             (SELECT tipo, classe, ano, mes, contagem FROM '''+schema+'''.indice_contagem_unificado
             where ano >= 2002)
             union all
             (SELECT tipo, classe, ano, mes, contagem FROM '''+schema+'''.indice_contagem_hat
             where ano >= 2002)
             )
             order by classe, tipo, ano, mes
             ''').format(autor=autor,reu=reu))

        return indice

    def get_indice_diario(self):
        schema = default_schema
        indice = self.execute_sql(
            '''(
            SELECT tipo, classe, data, contagem_amostra, media, mediana, desvio_padrao, percentile_10, percentile_75, percentile_90
	        FROM '''+schema+'''.indice_diario_agrupado_agregado
	        )
	        order by classe,tipo, data
            ''')

        return indice

    def get_indice_mensal(self,autor,reu):
        schema = default_schema

        indice = self.execute_sql((
            '''
            (
            (select tipo, classe, ano, mes, contagem_amostra, media, mediana, desvio_padrao, percentile_10, percentile_75, percentile_90 from '''+schema+'''.indice_mensal_agrupado_agregado
            where ano >= 2005 and classe <> 'ALUG')
            union ALL
            (select tipo, classe, ano, mes, contagem_amostra, media, mediana, desvio_padrao, percentile_10, percentile_75, percentile_90 from '''+schema+'''.indice_mensal_agrupado_pj_pf
            where ano >= 2005)
            union ALL
            (select tipo, classe, ano, mes, contagem_amostra, media, mediana, desvio_padrao, percentile_10, percentile_75, percentile_90 from '''+schema+'''.indice_mensal_agrupado_pjfin_pjnfin
            where ano >= 2005)
            union ALL
            (select tipo, classe, ano, mes, contagem_amostra, media, mediana, desvio_padrao, percentile_10, percentile_75, percentile_90 from '''+schema+'''.indice_mensal_agrupado_setor
            where ano >= 2005)
            )
            order by classe, tipo, ano, mes
            '''))

        return indice

    def listar_distribuicoes_sem_assunto(self,classe_processual=None, rank=0, fatia=1):
        try:
            if classe_processual:
                return self.listar(fatia=fatia, rank=rank,limit=1000).select().join(ClasseProcessual).switch(self._classe).join (DistribuicaoAssunto,join_type = JOIN.LEFT_OUTER).where(DistribuicaoAssunto.assunto == None,ClasseProcessual._nome_corrigido==classe_processual)# return self.listar (fatia=fatia, rank=rank).join (DistribuicaoAssunto).join (Assunto).select ().where (Assunto == '')
            else:
                return self.listar(fatia=fatia, rank=rank,limit=1000).select().join (DistribuicaoAssunto,join_type = JOIN.LEFT_OUTER).where(DistribuicaoAssunto.assunto == None)

        except Exception as e:
            print(str(e))

    def get_total_distribuicoes_t1(self):
        try:
            return self.execute_sql(''' select 'indicadores T1' as TIPO, ano,mes,sum(contagem) as distribuicoes from producao_indices.indice_contagem_unificado
                                        where tipo !~ 'RDO|RTE'
                                        group by ano ,mes
                                        order by ano,mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_distribuicoes_pj_t3(self):
        try:
            return self.execute_sql(''' select 'indicadores T3' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = true
                                        group by ano,mes) as x
                                        join
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD')
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_distribuicoes_pj_requerido_t4(self):
        try:
            return self.execute_sql(''' select 'indicadores T4' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        join producao_indices.tipo_parte tp on pd.tipo_parte_id = tp.id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = true and tp.nome ~ (( SELECT indice_tipo_parte.requerido FROM producao_indices.indice_tipo_parte))
                                        group by ano,mes) as x
                                        join
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = true
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_distribuicoes_pf_requerido_t5(self):
        try:
            return self.execute_sql(''' select 'indicadores T5' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        join producao_indices.tipo_parte tp on pd.tipo_parte_id = tp.id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = false and tp.nome ~ (( SELECT indice_tipo_parte.requerido FROM producao_indices.indice_tipo_parte))
                                        group by ano,mes) as x
                                        join
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = false
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_distribuicoes_pj_t6(self):
        try:
            return self.execute_sql(''' select 'indicadores T6' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        join producao_indices.tipo_parte tp on pd.tipo_parte_id = tp.id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD') and pd.pessoa_juridica = true and pd.banco = true
                                        group by ano,mes) as x
                                        join
                                        (SELECT
                                        date_part('year'::text, dist.data_distribuicao) AS ano,
                                        date_part('month'::text, dist.data_distribuicao) AS mes,
                                        count(pd.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.parte_distribuicao pd on dist.id = pd.distribuicao_id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD')
                                        group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_tamanho_medio_arquivo_txt_t7(self):
        try:
            return self.execute_sql(''' select 'indicadores T7' as TIPO,x.ano,x.mes, 1.0 * x.soma/b.count as tamanho_medio 
                                        from 
                                        (select sum(tamanho::DECIMAL) as soma,
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text, di.data) As mes 
                                        from producao_indices.arquivo arq
                                        join producao_indices.diario di on arq.diario_id = di.id
                                        where nome_arquivo ~ 'DJSP' and nome_arquivo !~ 'Empresarial' and di.data >= '1999-01-01'
                                        group by ano,mes) as x
                                        join (select count(*) as count, 
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text, di.data) As mes
                                        from producao_indices.arquivo arq 
                                        join producao_indices.diario di on arq.diario_id = di.id
                                        where nome_arquivo ~ 'DJSP' and nome_arquivo !~ 'Empresarial' and di.data >= '1999-01-01' group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_distribuicoes_data_distribuicao_menor_data_caderno_t10(self):
        try:
            return self.execute_sql(''' select 'indicadores T10' as TIPO,
                                        date_part('year'::text, di.data) AS ano_caderno,
                                        date_part('month'::text, di.data) AS mes_caderno,
                                        count(dist.id),
                                        date_part('year'::text, dist.data_distribuicao) AS ano_distri,
                                        date_part('month'::text, dist.data_distribuicao) AS mes_distr
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.caderno cad on dist.caderno_id = cad.id
                                        join producao_indices.diario di on cad.diario_id = di.id
                                        where dist.data_distribuicao < di.data and dist.data_distribuicao >= di.data - interval '4 month' and cp.nome_corrigido in ('USUCAP','TITEXEC','MONIT','BUSCAP','DESPEJO','ALUG','ALIM','RECJUD')
                                        group by date_part('month'::text, di.data),date_part('year'::text, di.data),date_part('month'::text, dist.data_distribuicao),
                                        date_part('year'::text, dist.data_distribuicao)
                                        order by ano_caderno, mes_caderno,ano_distri,mes_distr ''')
        except Exception as e:
            print(str(e))

    def get_porcentagem_distribuicao_data_posterior_t11(self):
        try:
            return self.execute_sql(''' select 'indicadores T11' as TIPO,x.ano, x.mes,1.0 * x.count/b.count as porcentagem from
                                        (select count(*),
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text,di.data) AS mes
                                        from producao_indices.distribuicao dist
                                        join producao_indices.caderno cad on dist.caderno_id = cad.id
                                        join producao_indices.diario di on cad.diario_id = di.id
                                        where dist.data_distribuicao > di.data
                                        group by ano,mes) as x
                                        join
                                        (select count(*),
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text,di.data) AS mes
                                        from producao_indices.distribuicao dist
                                        join producao_indices.caderno cad on dist.caderno_id = cad.id
                                        join producao_indices.diario di on cad.diario_id = di.id
                                         group by ano,mes) as b on x.ano=b.ano and x.mes=b.mes
                                        order by x.ano,x.mes ''')
        except Exception as e:
            print(str(e))

    def get_distribuicao_agrupado_por_data_t12(self):
        try:
            return self.execute_sql(''' SELECT 
                                        select 'indicadores T12',
                                        date_part('year'::text, di.data) AS ano,
                                        date_part('month'::text, di.data) AS mes,
                                        count(dist.id) as count
                                        from producao_indices.distribuicao dist
                                        join producao_indices.classe_processual cp on dist.classe_processual_id = cp.id
                                        join producao_indices.caderno cad on dist.caderno_id = cad.id
                                        join producao_indices.diario di on cad.diario_id = di.id
                                        where cp.nome_corrigido in ('USUCAP', 'TITEXEC', 'MONIT' ,'BUSCAP', 'DESPEJO', 'ALUG', 'ALIM' , 'RECJUD')
                                        group by ano,mes
                                        order by ano,mes ''')
        except Exception as e:
            print(str(e))