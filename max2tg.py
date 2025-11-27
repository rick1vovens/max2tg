#!/usr/bin/env python3
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from maxapi import MaxClient

MAX_PHONE = os.getenv("MAX_PHONE")
TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_SESSION = os.getenv("TG_SESSION", "")
TARGET_CHAT = os.getenv("TARGET_CHAT", "me")

async def main():
    tg = TelegramClient(StringSession(TG_SESSION), TG_API_ID, TG_API_HASH)
    await tg.start()

    max_client = MaxClient(MAX_PHONE)
    await max_client.connect()
    code = input("Код из Max: ")  # первый раз введёшь вручную в логах Render
    await max_client.sign_in(code)

    print("Всё подключено. Форвардим…")

    @max_client.on_message
    async def handler(msg):
        text = msg.text or "[медиа/файл]"
        sender = msg.sender.name if msg.sender else "?"
        chat = msg.chat.title if hasattr(msg.chat, "title") else "ЛС"
        await tg.send_message(TARGET_CHAT, f"{chat}\n{sender}\n\n{text}")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
