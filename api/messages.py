from fastapi import APIRouter, Depends, status, Query, HTTPException, Header, Security, Body
from api.models import delete_user, message_post
from messages.cache_ops import remove_from_cache
from messages.emai_scripts import send_email, wait_for_reply
from messages.telegram_scripts import send_message
import asyncio

messages_router = APIRouter(prefix='/messages')

tag = "Messages"

@messages_router.post(
    '/send-message',
    status_code=status.HTTP_200_OK,
    description='Отправка сообщений',
)
async def send(
    message_info: message_post
):
    if message_info.chat_type == 'tg':
        await send_message(message_info.username, message_info.text, message_info.message_id)
    elif message_info.chat_type == 'mail':
        await send_email(to_email=message_info.username, body=message_info.text, message_id=message_info.message_id, subject=message_info.subject)
    return {"status": "Message sent successfully"}  

@messages_router.post(
    '/delete-from-cache',
    status_code=status.HTTP_200_OK,
    description='Удаление пользователя из кеша'
)
async def delete(
    deleted_user: delete_user
):
    await remove_from_cache(deleted_user.username)