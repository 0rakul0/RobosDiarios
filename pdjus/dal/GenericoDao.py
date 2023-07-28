# -*- coding: utf-8 -*-
import abc
from _decimal import InvalidOperation
from datetime import datetime
from xml.dom import InvalidAccessErr

from decorator import contextmanager
from peewee import SENTINEL,chunked

from pdjus.conexao.Conexao import *
from pdjus.modelo import BaseClass
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.modelo.ProcTempTag import ProcTempTag
from util.StringUtil import remove_acentos, remove_varios_espacos



class GenericoDao(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, classe):
        self._classe = classe
        self._bd_cache = None

    @property
    def bd_cache(self):
        return self._bd_cache

    @bd_cache.setter
    def bd_cache(self, value):
        self._bd_cache = value

    def get_cached_object(self,key):
        if self.bd_cache:
            return self.bd_cache.get(key, None)
        self.new_cache_entry()
        return None

    def is_cached_object(self,obj):
        if self.get_cached_object(obj.get_key_cache()):
            return True
        else:
            return False

    def get_cached_items(self):
        if self.bd_cache:
            return self.bd_cache.items()
        return []

    def new_cache_entry(self):
        self.bd_cache = {}

    def add_to_cache(self,obj,key=None):
        if not self.bd_cache:
            self.new_cache_entry()

        if not key:
            self.bd_cache[obj.get_key_cache()] = obj
        else:
            self.bd_cache[key] = obj

    @contextmanager
    def auto_session(self,commit=False):
        sess = SessionDB().transaction
        try:
            yield sess
            if commit:
                sess.commit()
        except self._classe.DoesNotExist as e:
            sess.rollback()
            raise

    def save_cache(self):
        if self.bd_cache:
            for chave in self.bd_cache.copy().keys():
                obj = self.bd_cache.pop(chave, None)
                self.salvar(obj,commit=False)

    def get_por_id(self, id,cache = False):
        try:
            if cache:
                obj = self.get_cached_object(id)
                if not obj:
                    obj = self._classe.get(self._classe.id == id)
                    if obj:
                        self.add_to_cache(obj)
                return obj
            else:
                return self._classe.get(self._classe.id == id)
        except self._classe.DoesNotExist as e:
            return None

    def listar(self,cache = False,rank=0,fatia=1,limit=None,start=None, stop=None,tag=None,random=False,distinct=False):
        try:
            lista = None
            if cache:
                lista = self.get_cached_items()
            if not lista or len(lista) == 0:
                if tag:
                    tag = self._normalizar_marcador(tag)
                    try:
                        lista = self._classe.select().join(DadoExtraido).join(HistoricoDado).where(HistoricoDado.marcador == tag)
                    except:
                        try:
                            lista = self._classe.select().join(ProcTempTag).where(ProcTempTag.tag == tag)
                        except:
                            lista = self._classe.select()
                else:
                    lista = self._classe.select()
                if rank is not None and fatia is not None:
                    lista = lista.select().where(mod(self._classe.id, fatia) == rank)
                if limit:
                    lista = lista.limit(limit)
                if start:
                    lista = lista.offset(start)
                    if stop and stop - start > 0:
                        lista = lista.limit(stop - start)
                if random:
                    lista = lista.select().where(fn.Random() < 0.01)

                if distinct:
                    lista = lista.distinct()


            if cache:
                for obj in lista:
                    try:
                        self.add_to_cache(obj)
                    except:
                        self.add_to_cache(obj[1]) # TODO: GAMBIAARA FEITA PARA O TJSP POIS O OBJ ESTAVA VINDO COMO UMA TUPLA (DATA STR E OBJ PEEWEE)


            return lista

        except self._classe.DoesNotExist as e:
            return None


    def count(self):
        try:
            return self._classe.select().count()
        except self._classe.DoesNotExist as e:
            return None

    def count_tag(self, tag):
        try:
            tag = self._normalizar_marcador(tag)
            return self._classe.select().join(DadoExtraido).join(HistoricoDado).\
                where(HistoricoDado.marcador == tag).count()
        except self._classe.DoesNotExist as e:
            return None

    def commit(self):
        with self.auto_session() as session:
            session.commit()

    def execute_sql(self,sql,params=None,commit=SENTINEL):
        cursor = db.execute_sql(sql,params,commit)
        if not cursor.description:
            return None
        ncols = len(cursor.description)
        colnames = [cursor.description[i][0] for i in range(ncols)]
        results = []

        for row in cursor.fetchall():
            res = {}
            for i in range(ncols):
                res[colnames[i]] = row[i]
            results.append(res)
        return results

    def _normalizar_marcador(self, marcador):
        return remove_varios_espacos(remove_acentos(marcador.replace(' ', '_').upper()))



    def salvar_lote(self, objlist, caderno=None, tag=None,commit=True,salvar_estrangeiras=True,salvar_many_to_many=True):
        for obj in objlist:

            super(self.__class__, self).salvar(obj, caderno, tag, commit=False,salvar_estrangeiras=salvar_estrangeiras,salvar_many_to_many=salvar_many_to_many)
        if commit:
            self.commit()

    #@profile
    def inclui_data_atualizacao(self,obj):
        try:
            if obj and hasattr(obj, 'data_atualizacao'):
                hoje = datetime.today()
                obj.data_atualizacao = hoje
        except:
            print("Deu merda na data_atualização")

    def inclui_tag(self, caderno, dt_bd, tag):
        if hasattr(dt_bd, 'dado_extraido') and not type(dt_bd) is HistoricoDado:
            if not tag:
                raise InvalidAccessErr("ERRO: tentando salvar com a tag vazia!")
            tag = self._normalizar_marcador(tag)
            hoje = datetime.today()

            #NUNCA BUSCAR UM DADO EXTRAIDO NO BANCO, POIS É UMA CLASSE DE MAPEAMENTO. DEVE SER CRIADO SEMPRES UMA NOVA
            dado_extraido = dt_bd.dado_extraido

            if not dado_extraido:
                dado_extraido = DadoExtraido()
                dado_extraido.data_entrada = hoje
                dado_extraido.save()
                dt_bd.dado_extraido = dado_extraido

            try:
                hist = HistoricoDado.get(((((HistoricoDado.dado_extraido == dado_extraido) &
                                            (HistoricoDado.marcador == self._normalizar_marcador(tag))) &
                                           (HistoricoDado.data_extracao == hoje)) &
                                          ((HistoricoDado.caderno == None) | (HistoricoDado.caderno == caderno))))
            except HistoricoDado.DoesNotExist as e:
                hist = None
            # for historico in dt_bd.dado_extraido.historico:
            #     if historico.marcador == tag and historico.data_extracao == hoje and \
            #             (not historico.caderno or historico.caderno.id == caderno.id):
            #         hist = historico


            if not hist:
                hist = HistoricoDado()
                hist.marcador = tag
                hist.data_extracao = datetime.today()
                hist.dado_extraido = dado_extraido
                if caderno:
                    hist.caderno = caderno
                    hist.local_extracao = "DIARIO"
                else:
                    hist.local_extracao = "SISTEMA"
            elif not hist.caderno:
                hist.caderno = caderno

            hist.save()

    def salvar_lote_bulk(self, objlist):
        with db.atomic():
            self._classe.bulk_create(objlist,batch_size=1000)
            #super(self.__class__, self).bulk_create(objlist,batch_size=1000).execute()


    #@profile
    def salvar(self, obj, caderno=None, tag=None, commit=True, salvar_estrangeiras = True,salvar_many_to_many = True):

        if not obj or not obj.is_valido():
            if isinstance(obj,BaseClass):
                raise InvalidOperation("ESTÁ TENTANDO INSERIR OBJETOS INVÁLIDOS NO BANCO!")
            return
        try:
            self.inclui_tag(caderno, obj, tag)
            self.inclui_data_atualizacao(obj)
            obj.save()
            if salvar_estrangeiras:
                self.salvar_chaves_estrangeiras(obj, caderno, tag)
            if salvar_many_to_many:
                self.salvar_many_to_many(obj, caderno, tag)
            if commit:
                self.commit()
        except IntegrityError as e:
            self.rollback()
        except Exception as e:
            self.rollback()
            raise e

    def rollback(self):
        with self.auto_session() as session:
            session.rollback()

    def salvar_many_to_many(self, obj, caderno, tag):
        for nome_atributo, tipo_atributo in obj.__class__.__dict__.items():
            if isinstance(tipo_atributo, ManyToManyFieldDescriptorNew):
                try:
                    obj_child = getattr(obj, nome_atributo)
                    if obj_child and ((hasattr(obj_child, "id") and not obj_child.id) or not hasattr(obj_child, "id")):
                        self.inclui_tag(caderno, obj_child, tag)
                        obj_child.save()
                except DoesNotExist:
                    pass

    def salvar_chaves_estrangeiras(self, obj, caderno, tag):
        for nome_atributo, tipo_atributo in obj.__class__.__dict__.items():
            if isinstance(tipo_atributo, ForeignKeyAccessor):
                try:
                    obj_child = getattr(obj, nome_atributo)
                    if obj_child and ((hasattr(obj_child,"id") and not obj_child.id) or not hasattr(obj_child,"id")):
                        super(self.__class__, self).salvar(obj_child, caderno, tag, commit=False)
                        obj.save()
                    elif obj_child:
                        obj_child.save()
                        obj.save()
                except DoesNotExist:
                    pass

    def excluir(self,obj,commit=True):
        try:
            obj.delete_by_id(obj.id)
            if commit:
                self.commit()
        except self._classe.DoesNotExist as e:
            raise e

    def clear_cache(self):
        del self._bd_cache
        self.new_cache_entry()

    def mod(sslf, lhs, rhs):
        return Expression(lhs, OP.MOD, rhs)

    def not_exists(sslf, subquery):
        return ~fn.EXISTS(subquery)
