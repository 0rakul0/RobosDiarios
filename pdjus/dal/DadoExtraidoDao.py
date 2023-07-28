# -*- coding: utf-8 -*-
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.DadoExtraido import DadoExtraido
from util.StringUtil import remove_acentos,remove_varios_espacos



class DadoExtraidoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(DadoExtraidoDao, self).__init__(DadoExtraido)

