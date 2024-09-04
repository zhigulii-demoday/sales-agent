import asyncio
import datetime
import email
from email.message import EmailMessage
import aiosmtplib
from aioimaplib import IMAP4_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
import os
import requests
from . import models
from email.utils import parseaddr
from bs4 import BeautifulSoup

load_dotenv()

BASE_API_URL = os.getenv('BASE_API_URL')
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
APP_PASSWORD = os.getenv('APP_PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
SMTP_SERVER = os.getenv('SMTP_SERVER')
IMAP_PORT = int(os.getenv('IMAP_PORT'))
SMTP_PORT = int(os.getenv('SMTP_PORT'))

async def send_email(to_email: str, body: str, message_id: str | None = None, subject: str | None = None):
    msg = EmailMessage()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_email
    
    if subject:
        msg['Subject'] = subject

    if message_id:
        msg['In-Reply-To'] = message_id
        msg['References'] = message_id

    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        start_tls=True,
        username=EMAIL_ACCOUNT,
        password=APP_PASSWORD,
    )


async def process_message(data, client: IMAP4_SSL, from_email):
    msg = email.message_from_bytes(data[1])
    
    subject, encoding = decode_header(msg.get("Subject"))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding)

    from_header = msg.get("From")
    from_name, from_email_address = parseaddr(from_header)
    username = from_email_address  

    message_id = msg.get('Message-ID')

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
            elif content_type == "text/html":
                html_content = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.get_text()
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body = msg.get_payload(decode=True).decode()
        elif content_type == "text/html":
            html_content = msg.get_payload(decode=True).decode()
            soup = BeautifulSoup(html_content, 'html.parser')
            body = soup.get_text()

    request_body = models.AnswerModel(username, body, message_id, 'mail')

    # TODO: Добавить эндпоинт
    print(request_body)
    #requests.post(url=BASE_API_URL+'tg_endpoint', data=request_body.to_json())


async def monitor_inbox(from_email: str, client: IMAP4_SSL):
    await client.select('INBOX')
    await client.idle_start() 

    # TODO: установить временные рамки проверки почты
    while True:
        # Проверка почты каждые 5 сек (в тестовом режиме)
        await asyncio.sleep(5)

        client.idle_done()  

        # Смотрим инбокс за последние три дня
        three_days_ago = (datetime.date.today() - datetime.timedelta(days=3)).strftime('%d-%b-%Y')
        status, messages = await client.search('UNSEEN SINCE "{}" FROM "{}"'.format(three_days_ago, from_email))
        if status == 'OK' and messages[0]:
            # Письмо автоматически становится прочитанным и не выводится второй раз
            _, data = await client.fetch(int(messages[0].split()[-1]), '(RFC822)')
            await process_message(data, client, from_email)

        await client.idle_start()

# TODO: Установить таймаут ожидания ответа
async def wait_for_reply(from_email, timeout=300):
    # Таймаут ожидания ответа 300 сек
    client = IMAP4_SSL(IMAP_SERVER, timeout=timeout) 
    await client.wait_hello_from_server()
    await client.login(EMAIL_ACCOUNT, APP_PASSWORD)

    try:
        await asyncio.wait_for(monitor_inbox(from_email, client), timeout)
    except asyncio.TimeoutError:
        print(f"No reply received from {from_email} within the timeout period")
    except asyncio.CancelledError:
        print("Task was cancelled")
    finally:
        try:
            await client.logout()
        except Exception as e:
            print(f"Error during logout: {e}")

