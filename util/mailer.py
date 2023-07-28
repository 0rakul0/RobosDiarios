__author__ = 'B249025230'
from email.header import Header
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os

class Mailer(object):

    def __init__(self):
        self.__login = 'ipea.mailer@gmail.com'
        self.__password = 'maileripea'
        self.__to_addr_list = ['mateus.peixoto@ipea.gov.br', 'bruno.rocha@ipea.gov.br','carlos.honorio@ipea.gov.br', 'paulo.gomes@ipea.gov.br', 'joao.cruz@ipea.gov.br', 'ana.pierrout@ipea.gov.br']

    def send_email(self, assunto, msg, anexo=None, smtpserver='smtp.gmail.com:587',addr_list=None):
        message = MIMEMultipart('mixed')
        message['Subject'] = Header(assunto, "utf-8")
        message['From'] = self.__login
        if addr_list:
            message['To'] = ','.join(addr_list)
        else:
            message['To'] = ','.join(self.__to_addr_list)
        message.preamble = msg

        ctype, encoding = mimetypes.guess_type(anexo)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            fp = open(anexo)
            attachment = MIMEText(fp.read(), _subtype=subtype, _charset="UTF-8")
            fp.close()
        elif maintype == "image":
            fp = open(anexo, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype, _charset="UTF-8")
            fp.close()
        elif maintype == "audio":
            fp = open(anexo, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype, _charset="UTF-8")
            fp.close()
        else:
            fp = open(anexo, "rb")
            attachment = MIMEBase(maintype, subtype, _charset="UTF-8")
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
        conteudo =  MIMEText(msg.encode('utf-8'),'plain','utf-8')
        message.attach(conteudo)
        attachment.add_header("Content-Disposition", "attachment", filename=(Header(os.path.basename(anexo), 'utf-8').encode()))
        message.attach(attachment)

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(self.__login, self.__password)
        if addr_list:
            server.sendmail(self.__login, addr_list, message.as_string())
        else:
            server.sendmail(self.__login, self.__to_addr_list, message.as_string())
        server.quit()

