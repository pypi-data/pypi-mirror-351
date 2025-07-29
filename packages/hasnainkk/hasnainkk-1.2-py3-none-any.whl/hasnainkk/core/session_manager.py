from pyrogram import Client
from telegram.ext import Application
from typing import Optional

class SessionManager:
    def __init__(self, config: dict):
        self.config = config
        self.pyro_client: Optional[Client] = None
        self.ptb_app: Optional[Application] = None

    def init_pyrogram(self) -> Client:
        self.pyro_client = Client(
            "pyro_session",
            api_id=self.config["pyrogram"]["api_id"],
            api_hash=self.config["pyrogram"]["api_hash"],
            bot_token=self.config["pyrogram"]["bot_token"],
            sleep_threshold=0
        )
        return self.pyro_client

    def init_ptb(self) -> Application:
        self.ptb_app = Application.builder().token(
            self.config["ptb"]["bot_token"]
        ).build()
        self.ptb_app.rate_limiter = None
        return self.ptb_app

    async def start_sessions(self):
        if self.pyro_client:
            await self.pyro_client.start()
        if self.ptb_app:
            await self.ptb_app.initialize()

    async def stop_sessions(self):
        if self.pyro_client:
            await self.pyro_client.stop()
        if self.ptb_app:
            await self.ptb_app.shutdown()
