from typing import List, Union
from pyrogram import Client
from telegram.ext import Application
from ..handlers import BaseHandler

class Dispatcher:
    def __init__(self):
        self.pyro_handlers: List = []
        self.ptb_handlers: List = []

    def add_handler(self, handler: BaseHandler, 
                   library: str = "pyrogram"):
        """Add a handler for the specified library"""
        if library == "pyrogram":
            self.pyro_handlers.append(handler)
        elif library == "ptb":
            self.ptb_handlers.append(handler)
        else:
            raise ValueError("Invalid library specified. Use 'pyrogram' or 'ptb'")

    def register_all(self, 
                   pyro_client: Client = None, 
                   ptb_app: Application = None):
        """Register all handlers with their respective libraries"""
        for handler in self.pyro_handlers:
            if pyro_client:
                handler.register(pyro_client)
        
        for handler in self.ptb_handlers:
            if ptb_app:
                handler.register(ptb_app)
