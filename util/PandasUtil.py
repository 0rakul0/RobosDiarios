import pandas as pd
import numpy as np
from pdjus.conexao.Conexao import db
from pdjus.dal.JuntaComercialDao import JuntaComercialDao
from pdjus.modelo.JuntaComercial import JuntaComercial

juntaDao = JuntaComercialDao()
junta = JuntaComercial()
#junta = juntaDao.listar_por_data_caderno(data_caderno='2021-04-13')
# data = pd.DataFrame(junta.dicts())

# data.set_index(data['id'],inplace=True)
#
# data.to_csv("tabela_junta.csv",sep =';')
print('')
data = pd.read_csv("tabela_junta.csv",sep =',')

data.fillna('',inplace=True)

for valor in data.to_dict(orient='records'):
    junta.insert_many(valor).execute()

#data.to_sql(name='junta_comercial',con=db.connection(),if_exists='append')

print('')

#data['_texto]
#c data[data['_texto'] ==''].groupby('data').sum()

#data.groupby('data')['_texto'].apply(lambda x: x[x == ''].count()) #agrupa as vazias por data

#data[data['_texto'].str.match('RESTAURANTE') == True]  #Pesquisa por regex na coluna

#data[data['_texto'] ==''].groupby('data').count()['_texto'] agrupa os vazios por data,versão correta

#data.sort_values('empresa') ordernar o df
print('')