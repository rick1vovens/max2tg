#!/usr/bin/env python3
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
import logging

# Импорт из maxapi-python 1.1.x (новая структура)
from maxapi.client import MaxClient
from maxapi.types import Message

logging.basicConfig(level=logging.INFO)

# Переменные из Render Environment
MAX_PHONE = os.getenv("MAX_PHONE")
TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_SESSION = os.getenv("TG_SESSION", "")
TARGET_CHAT = os.getenv("TARGET_CHAT", "me")

async def main():
    if not all([MAX_PHONE, TG_API_ID, TG_API_HASH]):
        raise ValueError("Установи MAX_PHONE, TG_API_ID и TG_API_HASH в Environment Variables!")

    # Telegram клиент
    tg = TelegramClient(StringSession(TG_SESSION), TG_API_ID, TG_API_HASH)
    await tg.start()
    logging.info("Telegram подключён")

    # Max клиент (новый API)
    max_client = MaxClient(MAX_PHONE)
    await max_client.connect()
    
    if not TG_SESSION:
        # Первый запуск: ввод кода в логах Render
        code = input("Введи код из SMS в Max: ")
        await max_client.sign_in(code)
        logging.info("Max подключён")
        
        # Сохраняем сессию TG
        session_str = tg.session.save()
        logging.info(f"Сохрани эту строку в TG_SESSION: {session_str}")
    else:
        await max_client.sign_in()  # Автологин по сессии
        logging.info("Max подключён по сессии")

    logging.info(f"Форвардим всё из Max → {TARGET_CHAT}")

    @max_client.on(Message)
    async def handler(event: Message):
        text = event.message.text or "[медиа/файл/голосовое]"
        sender = event.sender.first_name or event.sender.username or "Неизвестно"
        chat = event.chat.title if hasattr(event.chat, 'title') else "Личка"
        
        forward_text = f"📱 {chat}\n👤 {sender}\n\n{text}"
        await tg.send_message(TARGET_CHAT, forward_text)
        logging.info(f"Форвард: {text[:50]}...")

    # Держим живым
    while True:
        await asyncio.sleep(3600)  # Проверка каждые 60 мин

if __name__ == "__main__":
    asyncio.run(main())
