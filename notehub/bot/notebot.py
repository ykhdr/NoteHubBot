import telebot

from bot import TOKEN
from bot.handlers.request_handler import RequestHandler


class NoteBot:
    def __init__(self):
        self.__bot = telebot.TeleBot(TOKEN)

    def __setup_handlers(self):
        self.__request_handler = RequestHandler(self.__bot)

    def run(self):
        self.__setup_handlers()
        self.__bot.infinity_polling()
