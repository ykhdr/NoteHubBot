import telebot
from telebot.types import Message
from bot.controllers.auth_controller import AuthController
from bot.controllers.dir_controller import DirectoryController
from bot.controllers.note_controller import NoteController


class RequestHandler:
    def __init__(self, bot: telebot.TeleBot):
        self.__bot = bot
        self.__auth_controller = AuthController()
        self.__note_controller = NoteController()
        self.__dir_controller = DirectoryController()

        self.__setup_message_handlers()

    def __setup_message_handlers(self):
        @self.__bot.message_handler(commands=['start'])
        def handle_start_message(message: Message):
            self.__bot.reply_to(message, message.text)

        @self.__bot.message_handler(func=lambda message: True)
        def handle_message(message : Message):
            self.__bot.reply_to(message, message.text)
