# -*- coding: utf-8 -*-

import json
import os
import sys
import errno
from datetime import datetime
import copy

from pdjus.conexao.Conexao import Singleton


class ConfigManager(object, metaclass=Singleton):

    def __init__(self):
        self.__config_robos = {
                          "DEJT": "..//..//dados//DEJT",
                          "TRT": "..//..//dados//DEJT",
                          "STJ": "..//..//dados//STJ",
                          "STF": "..//..//dados//STF",
                          "JUCESP": "..//..//dados//SP//JUCESP",
                          "TRTSP" : "..//..//dados//SP//TRTSP",
                          "DJBA": "..//..//dados//BA//DJBA",
                          "DJAL": "..//..//dados//AL//DJAL",
                          "DJES": "..//..//dados//ES//DJES",
                          "DJMG": "..//..//dados//MG//DJMG",
                          "DJGO": "..//..//dados//GO//DJGO",
                          "DJRR": "..//..//dados//RR//DJRR",
                          "DJRS": "..//..//dados//RS//DJRS",
                          "DJRN": "..//..//dados//RN//DJRN",
                          "DJSP": "..//..//dados//SP//DJSP",
                          "DJRJ": "..//..//dados//RJ//DJRJ",
                          "DJSC": "..//..//dados//SC//DJSC",
                          "DJMA": "..//..//dados//MA//DJMA",
                          "DJMS": "..//..//dados//MS//DJMS",
                          "DJPR": "..//..//dados//PR//DJPR",
                          "DJPB": "..//..//dados//PB//DJPB",
                          "DJCE": "..//..//dados//CE//DJCE",
                          "DJPE": "..//..//dados//PE//DJPE",
                          "DJAC": "..//..//dados//AC//DJAC",
                          "DJDF": "..//..//dados//DF//DJDF",
                          "DJAM": "..//..//dados//AM//DJAM",
                          "DJRO": "..//..//dados//RO//DJRO",
                          "DOU": "..//..//dados//DOU//DOU",
                          "DJPI": "..//..//dados//PI//DJPI",
                          "DJMT": "..//..//dados//MT//DJMT",
                          "DJTO": "..//..//dados//TO//DJTO",
                          "DJSE": "..//..//dados//SE//DJSE",
                          "JusBrasil": "..//..//dados//JUSBRASIL",
                          "TRF": "..//..//dados//TRF",
                          "TRF01": "..//..//dados//TRF//TRF01",
                          "TRF02": "..//..//dados//TRF//TRF02",
                          "TRF03": "..//..//dados//TRF//TRF03",
                          "TRF04": "..//..//dados//TRF//TRF04",
                          "TRF05": "..//..//dados//TRF//TRF05"
                        }

        self.__config_other = {
                          "RELATORIOS": "..//..//dados//RELATORIOS",
                          "RAIZ": "..//..//dados",
                          "maillogin": "ipea.mailer@gmail.com",
                          "mailpswd": "maileripea",
                          "mailfrom": "ipea.mailer@gmail.com",
                          #nao comitar linha 51
                          "logs": '..//dados//logs',
                          "LISTAS": "..//..//listas_tribunal"
                        }

        #self.__cfgname = os.path.join("..", "util", "cfg_servico.json")
        #self.__create_path(self.__cfgname)

        self.__max = 1024*1024*50
        self.__verify_os()

    def __verify_os(self):
        if sys.platform == 'linux': #coloca caminho absoluto para linux e mantém relativo para windows
            for k,v in self.__config_robos.items():
                self.__config_robos[k] = v.replace('..//..', '//mnt//dmlocal//')
            for k,v in self.__config_other.items():
                self.__config_other[k] = v.replace('..//..', '//mnt//dmlocal//')

    def __create_path(self, file):
        try:
            path, fname = os.path.split(file)

            if path.strip():
                os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def get_logpath(self, robo, logname):
        return os.path.join(self.le_config('logs'), logname)

    def __rotaciona_log(self, robo, log):
        logname = self.get_logpath(robo, log)
        self.__create_path(logname)

        if logname:
            if os.path.isfile(logname):
                if os.path.getsize(logname) > self.__max:
                    if not "erro" in log:
                        os.remove(logname)
                    else:
                        fileext = os.path.splitext(logname)

                        os.rename(logname, fileext[0] +
                                  datetime.now().strftime(".%d-%m-%Y_%H-%M-%S") + fileext[1])

    def get_full_config(self):
        '''cfg = None

        if os.path.isfile(self.__cfgname):
            try:
                file = open(self.__cfgname,mode='r')
                cfg = json.load(file)
                file.close()
            except Exception as e:
                os.remove(self.__cfgname)
        '''
        d = copy.deepcopy(self.__config_robos)
        d_other = copy.deepcopy(self.__config_other)
        d.update(d_other)

        return d

    def get_robot_config(self):
        '''cfg = None

        if os.path.isfile(self.__cfgname):
            try:
                file = open(self.__cfgname,mode='r')
                cfg = json.load(file)
                file.close()
            except Exception as e:
                os.remove(self.__cfgname)
        '''
        return copy.deepcopy(self.__config_robos)

    def escreve_log(self, linha, robo=None, log=None, verbose=True):
        if not robo and not log:
            print(linha)
            return

        logname = self.get_logpath(robo, log)
        self.__create_path(logname)
        self.__rotaciona_log(robo, log)
        if not logname:
            logname = log
        if logname:
            if not os.path.isfile(logname):
                open(logname, 'w').close()
            file = open(logname,'a',encoding='UTF8')
            log = file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " +  linha.strip() + '\n')
            if verbose:
                print(linha)
            file.close()

    def le_log(self, robo, log):
        logname = self.get_logpath(robo, log)
        self.__create_path(logname)

        conteudo = ""

        if logname:
            if os.path.isfile(logname):
                file = open(logname,'r')
                conteudo = file.readlines()
                file.close()

            return conteudo
        return None

    def le_config(self, config):
        cfg = None

        arqcfg = self.get_full_config()

        if arqcfg is not None:
            if config in arqcfg:
                cfg = arqcfg[config]

        return cfg

    def arquivo_suportado_extrator(self, nome):
        if not nome:
            return False
        return nome.endswith('.txt') or nome.endswith('.html') or nome.endswith('.htm') or nome.endswith('.ata')
