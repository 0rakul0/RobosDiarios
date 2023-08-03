# Script de Coleta de dados em Estrutura de Diretórios

Este é um script em Python que percorre uma estrutura de diretórios em busca de arquivos em determinados formatos e gera um arquivo CSV com os dados coletados. Ele inclui funcionalidades para filtrar os dados por ano e mês.

## Etapas a fazer

- Clone este repositório para o seu ambiente local.
- Configure o diretório raiz e os tipos de arquivos desejados no código.
- Execute o arquivo `listar_arquivos.py`.

## Filtragem de dados por ano

O script oferece duas opções para filtrar os dados coletados:

1. Utilizando `dados`: Se você utilizar a variável `dados`, o script trará o caminho com o último ano existente dentro da pasta, independente do ano. Ou seja, todos os anos encontrados serão incluídos no arquivo CSV.

2. Utilizando `dados_atualizados`: Se você optar pela variável `dados_atualizados`, o script trará apenas os caminhos dos estados que possuem a pasta de ano 2023. Ou seja, somente os dados referentes a esse ano serão incluídos no arquivo CSV.

Para utilizar as opções acima, siga as instruções abaixo:

- Para trazer todos os anos encontrados, comente a linha `dados_atualizados = ...` e descomente a linha `dados = ...`.
- Para trazer apenas os dados referentes ao ano 2023, comente a linha `dados = ...` e descomente a linha `dados_atualizados = ...`.
- Salve as alterações e execute novamente o arquivo `lista_ultimo_arquivo.py`.

## Funcionalidades

O script irá percorrer a estrutura de diretórios a partir do caminho específico e coletar dados de acordo com os critérios definidos. Em seguida, ele imprimirá os caminhos dos dados coletados e gerará um arquivo CSV com os resultados.

## Personalização

Você pode personalizar o script de acordo com suas necessidades. Algumas possíveis modificações incluem:

- Adicionar novos tipos de arquivo na lista `tipo_arquivos_pastas` para coletar diferentes tipos de arquivos.
- Modificar as siglas dos estados na lista `siglas_estados` para se adequar ao seu conjunto de diretórios.

## Funções existentes

- listar_arquivos.py
  - obter_ano_pasta
  - obter_pastas_ano
  - obter_pasta_recente
  - obter_caminhos_meses
  - percorrer_pastas

- util
  - gerar_csv.py
    - gerar_csv
      - gerar_csv
    - verificar_data_modificacoes
      - verificar_data_modificacao
    - manipular_arquivos
      - listar_arquivos
      - criar_pastas_anos
      - criar_pastas_meses

## Alterações
#### Data

| Data       | Alteração                                                                             | Concluído |
|------------|---------------------------------------------------------------------------------------|-----------|
| 24/07/2023 | Foi alterado csv, add uma função para último mês e especificado ordem do arquivo csv. | Ok        |
| 28/07/2023 | Criado funcao para obter estados nao atualizados                                      | Ok        |
