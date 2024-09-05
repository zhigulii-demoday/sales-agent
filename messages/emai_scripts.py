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

CACHE_FILE = 'email_cache.txt'

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

    await update_cache(to_email)


async def update_cache(to_email):
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'w') as f:
            f.write(to_email + '\n')
    else:
        with open(CACHE_FILE, 'r') as f:
            emails = f.read().splitlines()

        if to_email not in emails:
            with open(CACHE_FILE, 'a') as f:
                f.write(to_email + '\n')


async def load_cache():
    if not os.path.exists(CACHE_FILE):
        return []
    
    with open(CACHE_FILE, 'r') as f:
        return f.read().splitlines()



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


async def monitor_inbox(client: IMAP4_SSL):
    await client.select('INBOX')

    cache_emails = await load_cache()
    if not cache_emails:
        print("No emails in cache.")
        return

    while True:
        print("Waiting for new messages...")
        try:

            # Ждем некоторое время (например, 5 минут)
            await asyncio.sleep(300)

            print("Checking for new messages...")
            three_days_ago = (datetime.date.today() - datetime.timedelta(days=3)).strftime('%d-%b-%Y')
            status, messages = await client.search(f'UNSEEN SINCE "{three_days_ago}"')

            if status != 'OK' or not messages or not messages[0]:
                print("No new messages or search failed.")
                continue

            # Перебираем все сообщения
            for num in messages[0].split():
                fetch_status, data = await client.fetch(int(num), '(RFC822)')

                if fetch_status != 'OK' or not data:
                    print(f"Failed to fetch message {num}")
                    continue

                msg = email.message_from_bytes(data[1])
                from_header = msg.get("From")
                from_name, from_email_address = parseaddr(from_header)

                # Проверяем, есть ли отправитель в кэше
                if from_email_address in cache_emails:
                    await process_message(data, client, from_email_address)

        except asyncio.CancelledError:
            print("Task was cancelled.")
            await client.idle_done()  
            break
        except Exception as e:
            print(f"Error during monitoring inbox: {e}")


async def wait_for_reply():
    client = IMAP4_SSL(IMAP_SERVER)
    await client.wait_hello_from_server()
    await client.login(EMAIL_ACCOUNT, APP_PASSWORD)

    try:
        await monitor_inbox(client)  
    except asyncio.CancelledError:
        print("Task was cancelled.")
    except Exception as e:
        print(f"Error during wait_for_reply: {e}")
    finally:
        try:
            await client.logout()
        except Exception as e:
            print(f"Error during logout: {e}")



