import os

import telebot

from bot.controllers.auth_controller import AuthController
from bot.controllers.dir_controller import DirectoryController
from bot.controllers.note_controller import NoteController
from bot.controllers.storage_msg_collector import StorageMessageCollector
from bot.handlers.command_handler import CommandHandler
from bot.handlers.dir_op_handler import DirectoryOperationsHandler
from bot.handlers.note_op_handler import NoteOperationsHandler
from bot.handlers.note_share_inline_handler import NoteShareInlineHandler
from bot.handlers.reply_handler import ReplyHandler


class NoteBot:
    __TOKEN = os.getenv('TOKEN')

    def __init__(self):
        self.__bot = telebot.TeleBot(NoteBot.__TOKEN)

        dir_controller = DirectoryController()
        note_controller = NoteController()
        auth_controller = AuthController()
        storage_msg_collector = StorageMessageCollector(dir_controller, note_controller)

        self.__command_handler = CommandHandler(self.__bot, auth_controller, dir_controller, storage_msg_collector)
        self.__dir_op_handler = DirectoryOperationsHandler(self.__bot, dir_controller, note_controller,
                                                           storage_msg_collector)
        self.__note_op_handler = NoteOperationsHandler(self.__bot, dir_controller, note_controller,
                                                       storage_msg_collector)
        self.__reply_handler = ReplyHandler(self.__bot, note_controller, dir_controller, storage_msg_collector)
        self.__note_share_inline_handler = NoteShareInlineHandler(self.__bot, note_controller)

        print('NoteBot have been inited')

    def __setup_handlers(self):
        self.__command_handler.setup_handler()
        self.__dir_op_handler.setup_handler()
        self.__note_op_handler.setup_handler()
        self.__reply_handler.setup_handler()
        self.__note_share_inline_handler.setup_handler()

        print('Handlers have been setuped')

    def run(self):
        self.__setup_handlers()
        print('NoteBot ran')
        self.__bot.infinity_polling()
