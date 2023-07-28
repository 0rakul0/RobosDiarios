#TODO Depreciado

'''# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
import sys

from util.ConfigManager import ConfigManager
import traceback

log = "log_servico.txt"
erro = "erro_servico.txt"
diretorio = "RAIZ"


def executa_robo(class_name):
    try:
        mod = __import__(class_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        method = "download_atualizacao_diaria"
        obj = cls()
        return getattr(obj, method)()
    except:
        ConfigManager().escreve_log(class_name + ": " + traceback.format_exc(), diretorio, erro)

def inicia_robos():
    #pwd = os.path.join(os.path.dirname(__file__))

    ConfigManager().escreve_log("Iniciando robos...", diretorio, log)

    st = datetime.now()

    #Usar os métodos abaixo para debugh individual de cada robô
    #executa_robo("DEJT")
    #executa_robo("DJPI")
    #executa_robo("DJRJ")
    #executa_robo("DJMG")
    #executa_robo("DJSC")
    #executa_robo("DJMS")
    #executa_robo("DJBA")
    #executa_robo("DJPR")
    #executa_robo("DJDF")
    #executa_robo("DJPE")
    #executa_robo("DJCE")
    #executa_robo("DOU")
    #executa_robo("DJRS")
    #executa_robo("DJSP")
    #executa_robo("JusBrasil")
    #executa_robo("TRF")
    #executa_robo("STJ")
    #executa_robo("JUCESP")

    ConfigManager().escreve_log("Execução em {}.".format(str(datetime.now() - st)), diretorio, log)
    ConfigManager().escreve_log("Execução concluída.", diretorio, log)

if __name__ == '__main__':
    inicia_robos()'''
