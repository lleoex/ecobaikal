import smtplib as smtp
from email.message import EmailMessage
import mimetypes

import os

from settings import Settings
sets = Settings()

def sendmail(subj:str, body:str, attacments:list):
    login = 'ecomag.baikal@iwp.ru'
    _from = 'ecomag.baikal@iwp.ru'
    _to = sets.emails_d
    #_to = ['gonchukovlv@yandex.ru', 'gonchukov-lv@ferhri.ru']
    #passwd = 'T1Wcy^,)FCxZ}!m'
    passwd = 'jxnejmhomhlvarjc'
    #message = body

    msg = EmailMessage()
    msg['Subject'] = subj
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = _from
    msg['To'] = _to
    #msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'
    msg.set_content(body)

    # Open the files in binary mode.  You can also omit the subtype
    # if you want MIMEImage to guess it.
    for path in attacments:
        filename = os.path.split(path)[-1]
        if not os.path.isfile(path):
            continue
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(path, 'rb') as fp:
            msg.add_attachment(fp.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=filename)

    server = smtp.SMTP_SSL('smtp.yandex.ru')
    #server.set_debuglevel(1)
    server.ehlo(_from)
    server.login(login, passwd)
    server.auth_plain()
    server.send_message(msg)
    server.quit()

