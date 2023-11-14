import telebot
from telebot.types import Message

from bot.controllers.auth_controller import AuthController
from bot.controllers.dir_controller import DirectoryController
from bot.controllers.keyboard_controller import KeyboardController
from bot.controllers.storage_msg_collector import StorageMessageCollector
from bot.handlers.handler import Handler
from bot.models.bot_types import BotTypes
from bot.models.messages import Messages


class CommandHandler(Handler):
    def __init__(self, bot: telebot.TeleBot, auth_controller: AuthController, dir_controller: DirectoryController,
                 storage_msg_collector: StorageMessageCollector):
        self.__bot = bot
        self.__auth_controller = auth_controller
        self.__dir_controller = dir_controller
        self.__storage_msg_collector = storage_msg_collector

    def setup_handler(self):
        @self.__bot.message_handler(commands=['start'])
        def handle_start_message(message: Message):
            # if self.__auth_controller.get_user(message.from_user.id):
            #     return
            chat_id = message.chat.id
            user_id = message.from_user.id

            self.__bot.send_message(chat_id, Messages.HELLO_MESSAGE,
                                    reply_markup=KeyboardController.create_directory_reply_keyboard(
                                        BotTypes.DIRS_STORAGE_TYPE))
            self.__auth_controller.create_user(chat_id, user_id)
            dir = self.__dir_controller.create_root(chat_id)

            if not dir:
                dir = self.__dir_controller.get_root_directory(chat_id)

            self.__dir_controller.create_user_current_directory(chat_id, dir.id)

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, dir.id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE, 0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)
