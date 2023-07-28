from peewee import *
from peewee import Expression, OP, ManyToManyQuery, ManyToManyField, ManyToManyFieldAccessor,JOIN
from playhouse.pool import PooledPostgresqlExtDatabase
from playhouse.sqlite_ext import SqliteExtDatabase
from peewee import *
from peewee import Expression, ForeignKeyAccessor

OP['MOD'] = 'mod'
OP['NEG_REGEX'] = 'neg_regex'
OP['NOT_EXISTS'] = 'not_exists'

def mod(lhs, rhs):
    return Expression(lhs, OP.MOD, rhs)
def neg_regexp(field, value):
    return Expression(field,OP.NEG_REGEX,value)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ManyToManyList(list):
    def __init__(self,instance,field_descriptor,rel_model):
        self.instance = instance
        self.field_descriptor = field_descriptor
        self.rel_model = rel_model

    def save(self):
        query = ManyToManyQuery(self.instance, self.field_descriptor, self.rel_model)
        list_database = self.field_descriptor.get_database(self.instance)
        for obj in list(self):
            if not obj in list_database:
                query.add(obj)



#class ManyToManyFieldDescriptorNew(ManyToManyFieldDescriptor):
class ManyToManyFieldDescriptorNew(ManyToManyFieldAccessor):

    def __init__(self, model, field, name):
        #super(ManyToManyFieldAccessor, self).__init__(model, field, name)
        self.model = field.model
        self.rel_model = field.rel_model
        self.through_model = field.get_through_model()
        self.src_fk = self.through_model._meta.model_refs[self.model][0]
        self.dest_fk = self.through_model._meta.model_refs[self.rel_model][0]
    #def __init__(self, field):
        self.field = field
        self.lista = field.lista
        #super(ManyToManyFieldDescriptorNew, self).__init__(field)
        super(ManyToManyFieldDescriptorNew, self).__init__(model, field, name)

    def get_database(self,instance):
        #return (ManyToManyQuery(instance, self, self.rel_model).select().join(self.through_model).join(self.model).where(self.src_fk == instance))
        return (self, self.rel_model.select().join(self.through_model).join(self.model).where(self.src_fk == instance))[1]

    #def __get__(self, instance, instance_type=None):
    def __get__(self, instance, instance_type=None, force_query=False):
        if instance is not None:
            ids = id(instance)
            if not ids in self.lista:
                self.lista[ids] = ManyToManyList(instance, self, self.rel_model)
            if len(self.lista[ids]) == 0:
                objs = list(( self, self.rel_model.select().join(self.through_model).join(self.model).where(self.src_fk == instance))[1])
                #(ManyToManyQuery(instance, self, self.rel_model).select().join(self.through_model).join(self.model).where(self.src_fk == instance))
                for obj in objs:
                    if obj and obj.id and obj not in self.lista[ids]:
                        self.lista[ids].append(obj)
            return self.lista[ids]
        return self.field

    def __set__(self, instance, value):
        self.lista = self.__get__(instance).append(value)
        #query.add(value, clear_existing=True)

class ManyToMany(ManyToManyField):
    accessor_class = ManyToManyFieldDescriptorNew
    lista ={}
    def __int__(self, rel_model, related_name=None, through_model=None,
                 _is_backref=False):
        #self.lista = {}
        super(ManyToMany,self).__init__(rel_model, related_name, through_model,_is_backref)

    def _get_descriptor(self):
        if not hasattr(self,"lista"):
            self.lista = {}
        return ManyToManyFieldDescriptorNew(self)