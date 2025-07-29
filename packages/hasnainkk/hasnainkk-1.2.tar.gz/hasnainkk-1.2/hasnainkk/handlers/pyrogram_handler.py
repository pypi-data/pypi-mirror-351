from .base_handler import BaseHandler
from pyrogram import Client
from pyrogram.types import Message
from typing import Any, Dict

class PyrogramHandler(BaseHandler):
    def register(self, client: Client):
        """Register Pyrogram handler"""
        @client.on_message()
        async def handle_message(client: Client, message: Message):
            await self.handle(client, message)

    async def handle(self, client: Client, message: Message):
        """Default Pyrogram message handler"""
        await message.reply("Processed by Pyrogram handler")
