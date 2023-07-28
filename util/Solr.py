import requests

urlsolr = "http://dm-new:8983/solr/core_diarios/"

def consulta_diarios(npu):
    url =  urlsolr + "select?q=_text_:{npu}&rows=10&sort=id asc"
    s = requests.Session()
    jresultado = s.get(url.format(npu=npu), verify=False)
    return jresultado.json()['response']['docs']

def consulta_diarios_sem_texto(npu):
    url =  urlsolr + "select?q=_text_:{npu}&rows=10&fl=id"
    s = requests.Session()
    jresultado = s.get(url.format(npu=npu), verify=False)
    return jresultado.json()['response']['docs']