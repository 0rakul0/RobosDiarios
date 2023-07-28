import os
from datetime import datetime
import re
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format

def converte_pdf(caminho_arquivo, nome_bucket):
    #Bibliotecas Necessárias
    # pip install --upgrade pip --user
    # pip install --upgrade google-auth
    # pip install --upgrade pyasn1-modules
    # pip install --upgrade google-cloud-storage
    # pip install --upgrade google-cloud-vision
    # pip uninstall protobuf
    # pip install protobuf==3.6.0 (É necessário porque a versão mais atual deu conflito no meu pc. Mas carece de testes

    #Para autencitação no google vision,necessário o arquivo json
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/mnt/dmlocal/projetos/Master/util/chrome-insight-278413-8ea7e08d8eb1.json'

    #Upload do arquivo no servidor do google
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(nome_bucket)
    blob = bucket.blob(os.path.basename(caminho_arquivo))
    blob.upload_from_filename(caminho_arquivo)

    #Iniciação da aplicação,
    client = vision.ImageAnnotatorClient()
    batch_size = 20
    mime_type = 'application/pdf'

    feature = vision.types.Feature(
        type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

    #pdf que ele vai enviar para o vision
    gcs_source_uri = 'gs://{}/'.format(nome_bucket)+os.path.basename(caminho_arquivo)
    gcs_source = vision.types.GcsSource(uri=gcs_source_uri)
    input_config = vision.types.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    #json de destino,o vision cria a conversão em arquivos .json
    gcs_destination_uri = 'gs://{}/'.format(nome_bucket)+ os.path.basename(caminho_arquivo).replace('.pdf','') + 'out'
    gcs_destination = vision.types.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.types.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.types.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config)

    operation = client.async_batch_annotate_files(requests=[async_request])
    operation.result(timeout=180)

    #uma vez salvo os json no servidor,precisamos coletá-los de lá para extrair o texto
    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    # Aqui ele vai buscar do servidor todos os json que tiverem o mesmo prefixo,ou seja o nome do arquivo enviado (necessário testar se pode haver conflito)
    blob_list = list(bucket.list_blobs(prefix=prefix))
    # print('Output files:')
    # for blob in blob_list:
    #     print(blob.name)

    output = blob_list[0]
    json_string = output.download_as_string()
    response = json_format.Parse(
        json_string, vision.types.AnnotateFileResponse())

    first_page_response = response.responses[0]
    annotation = first_page_response.full_text_annotation

    #aqui ele vai juntar os textos dos arquivos json em uma variável
    texto = ''
    for annotation in response.responses:
        texto += annotation.full_text_annotation.text+"\n"
        #print(annotation.full_text_annotation.text+"\n")


    # breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType
    # paragraphs = []
    # lines = []
    # for page in annotation.pages:
    #     for block in page.blocks:
    #         for paragraph in block.paragraphs:
    #             para = ""
    #             line = ""
    #             for word in paragraph.words:
    #                 for symbol in word.symbols:
    #                     line += symbol.text
    #                     if symbol.property.detected_break.type == breaks.SPACE:
    #                         line += ' '
    #                     if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
    #                         line += ' '
    #                         lines.append(line)
    #                         para += line
    #                         line = ''
    #                     if symbol.property.detected_break.type == breaks.LINE_BREAK:
    #                         lines.append(line)
    #                         para += line
    #                         line = ''
    #             paragraphs.append(para)
    #
    # print(paragraphs)
    # print(lines)
    list_total_blobs = list(bucket.list_blobs())
    if len(list_total_blobs) >= 100:
        bucket.delete_blobs(list_total_blobs)
        print('{} - Apagando {} arquivos do dentro do bucket {} GogleVisonOCR'.format(datetime.now(), len(list_total_blobs), nome_bucket))

    return texto