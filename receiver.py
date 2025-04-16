import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
import base64
import settings


def clean(text)->str:
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def receivemail() -> (datetime, str):
    # account credentials
    login = 'ecomag.baikal@iwp.ru'
    passwd = 'uhwifsunnyqtseqk'
    # use your email provider's IMAP server, you can look for your provider's IMAP server on Google
    # or check this page: https://www.systoolsgroup.com/imap/
    # for office 365, it's this:
    imap_server = "imap.yandex.ru"
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(login, passwd)

    status, messages = imap.select("INBOX")

    messages = int(messages[0])
    N = 10

    maxDt = datetime(2020,1,1)
    lastFile=''

    for i in range(messages, messages - N, -1):
    #for i in range(1, 4, 1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_disposition != 'None':
                            if "attachment" in content_disposition:
                                filename=''
                                dt=''
                                for line in content_disposition.split('\r\n'):
                                    if "filename" in line:
                                        fname_b64 = line.split('"')[1]
                                        if isinstance(fname_b64, bytes) or fname_b64.startswith('='):
                                            dstr = base64.b64decode(fname_b64.split('?')[-2])
                                            filename = dstr.decode('windows-1251')
                                        else:
                                            filename = fname_b64
                                        print(filename)
                                    elif 'modification-date' in line:
                                        dt_b64 = line.split('"')[1]
                                        dt = datetime.strptime(dt_b64,'%a, %d %b %Y %H:%M:%S GMT')
                                        print(dt_b64)
                                if filename:
                                    sets = settings.Settings()
                                    path = os.path.join(sets.EMAIL_XLS_DIR,f'{dt.strftime("%Y%m%d_%H%M")}_{filename}')
                                    open(path, "wb").write(part.get_payload(decode=True))
                                    if dt > maxDt:
                                        maxDt=dt
                                        lastFile = path
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass





                print("=" * 100)
    # close the connection and logout
    imap.close()
    imap.logout()

    return maxDt, lastFile