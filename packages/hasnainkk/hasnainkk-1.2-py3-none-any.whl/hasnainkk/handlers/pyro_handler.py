from .base_handler import BaseHandler
from pyrogram.types import Message

class PyroHandler(BaseHandler):
    def register(self, client):
        @client.on_message()
        async def wrapper(_, message: Message):
            await self.handle(client, message)

    async def handle(self, client, message: Message):
        """Override this method in child classes"""
        await message.reply("Default Pyro handler response")
