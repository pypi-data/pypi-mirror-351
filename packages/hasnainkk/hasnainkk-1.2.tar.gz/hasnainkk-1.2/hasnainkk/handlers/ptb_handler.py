from .base_handler import BaseHandler
from telegram import Update
from telegram.ext import ContextTypes

class PTBHandler(BaseHandler):
    def register(self, app):
        app.add_handler(app.message_handler()(self.handle))

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Override this method in child classes"""
        await update.message.reply_text("Default PTB handler response")
