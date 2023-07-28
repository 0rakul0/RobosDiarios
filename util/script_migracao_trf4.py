from pdjus.service.MapaProcessoService import MapaProcessoService
from pdjus.service.ProcessoService import ProcessoService
from pdjus.modelo.MapaProcesso import MapaProcesso

print("Vai começar a migracao HA HA HA HA HA")

processo_service = ProcessoService()
query = processo_service.dao.execute_sql("(select proc.npu as npu,proc.numero_processo as numero_processo,proc.grau as grau,c.nome as classe,ass.nome as assunto "
                                 "from desenv_trf4.processo proc "
                                 "left join producao_indices.mapa_processo p on p.npu = proc.npu or p.numero_processo = proc.numero_processo "
                                 "join desenv_trf4.classe_processual c on c.id=proc.classe_processual_id "
                                 "join desenv_trf4.processo_assunto procass on procass.processo_id = proc.id "
                                 "join desenv_trf4.assunto as ass on procass.assunto_id = ass.id "
                                 "where p.id is Null and random() < 0.01 limit 1000)")
while len(query) > 0 :
    mapa_processo_service = MapaProcessoService()
    i=0
    for item in query:
        try:
            mapa_processo = mapa_processo_service.dao.get_por_numero_processo_ou_npu(item['npu'] if item['npu'] else item['numero_processo'] if item['numero_processo'] else None,grau=item['grau'])
            if not mapa_processo:
                mapa_processo = MapaProcesso()
                print("não tem no banco !!!!")
                mapa_processo.npu = item['npu'] if item['npu'] else None
                mapa_processo.numero_processo = item['numero_processo'] if item['numero_processo'] else None
                mapa_processo.grau = item['grau'] if item['grau'] else None

                if item["classe"]:
                    mapa_processo_service.seta_classe_processual(mapa_processo,item["classe"])

                if item["assunto"]:
                    mapa_processo_service.seta_assunto(mapa_processo,item["assunto"])

                mapa_processo_service.salvar(mapa_processo,tag= "TRF04",commit=False)
                if i % 50 == 0:
                    mapa_processo_service.dao.commit()
                    print("COMMITOU")
                print("Npu inserido: " + item['npu'] if item['npu'] else item['numero_processo'] if item['numero_processo'] else "")
                i+=1
        except Exception as e:
            print("Erro "+str(e))

    query = processo_service.dao.execute_sql(
        "(select proc.npu as npu,proc.numero_processo as numero_processo,proc.grau as grau,c.nome as classe,ass.nome as assunto "
        "from desenv_trf4.processo proc "
        "left join producao_indices.mapa_processo p on p.npu = proc.npu or p.numero_processo = proc.numero_processo "
        "join desenv_trf4.classe_processual c on c.id=proc.classe_processual_id "
        "join desenv_trf4.processo_assunto procass on procass.processo_id = proc.id "
        "join desenv_trf4.assunto as ass on procass.assunto_id = ass.id "
        "where p.id is Null and random() < 0.01 limit 1000)")

