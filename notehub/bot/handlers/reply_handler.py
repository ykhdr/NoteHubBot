import re

import telebot
from telebot.types import Message, InputTextMessageContent, InlineQueryResultArticle

from bot.controllers.dir_controller import DirectoryController
from bot.controllers.keyboard_controller import KeyboardController
from bot.controllers.note_controller import NoteController
from bot.controllers.storage_msg_collector import StorageMessageCollector
from bot.handlers.handler import Handler
from bot.models.bot_types import BotTypes
from bot.models.entities.directory import Directory


class ReplyHandler(Handler):
    def __init__(self, bot: telebot.TeleBot, note_controller: NoteController, dir_controller: DirectoryController,
                 storage_msg_collector: StorageMessageCollector):
        self.__bot = bot
        self.__dir_controller = dir_controller
        self.__note_controller = note_controller
        self.__storage_msg_collector = storage_msg_collector

    def setup_handler(self):

        @self.__bot.message_handler(func=lambda message: message.text in BotTypes.get_reply_commands_list())
        def handle_reply_buttons_message(message: Message):
            chat_id = message.chat.id

            if message.text == BotTypes.DELETE_DIR_BUTTON_TEXT:
                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                children = self.__dir_controller.get_child_directories(chat_id, cur_dir.id)
                notes = self.__note_controller.get_notes_in_directory(chat_id, cur_dir.id)

                if cur_dir.parent_dir_id is None:
                    self.__bot.send_message(chat_id, 'Корневую директорию нельзя удалить')

                if children or notes:
                    self.__bot.send_message(chat_id, 'Директория не пуста, очистите директорию перед удалением')
                else:
                    self.__delete_directory(chat_id)

            elif message.text == BotTypes.CREATE_DIR_BUTTON_TEXT:
                self.__bot.send_message(chat_id, 'Введите название директории:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)

            elif message.text == BotTypes.CHANGE_TO_NOTES_BUTTON_TEXT:
                reply_keyboard = KeyboardController.create_directory_reply_keyboard(BotTypes.NOTES_STORAGE_TYPE)
                self.__bot.send_message(chat_id, 'Вы сменили показ на заметки', reply_markup=reply_keyboard)

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                      BotTypes.NOTES_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id, text, reply_markup=keyboard)

            elif message.text == BotTypes.CHANGE_TO_DIRS_BUTTON_TEXT:
                reply_keyboard = KeyboardController.create_directory_reply_keyboard(BotTypes.DIRS_STORAGE_TYPE)
                self.__bot.send_message(chat_id, 'Вы сменили показ на директории', reply_markup=reply_keyboard)

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                      BotTypes.DIRS_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id, text, reply_markup=keyboard)

            elif message.text == BotTypes.CREATE_NOTE_BUTTON_TEXT:
                msg = self.__bot.send_message(chat_id, 'Введите название заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name)

            elif message.text == BotTypes.RENAME_DIR_BUTTON_TEXT:
                self.__bot.send_message(chat_id, 'Введите название директории:')
                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_directory, cur_dir.id)

    def __handle_rename_directory(self, message: Message, dir_id):
        chat_id = message.chat.id
        text = message.text

        if text in BotTypes.get_reply_commands_list():
            self.__bot.send_message(chat_id, 'Некорректное название для директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)
            return

        elif len(text) >= 30:
            self.__bot.send_message(chat_id, 'Слишком длинное название, используйте название короче 30 символов')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name)
            return

        elif self.__dir_controller.is_directory_in_cur_parent_exists(chat_id, text):
            self.__bot.send_message(chat_id, 'Директория с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)
            return

        self.__dir_controller.rename_directory(dir_id, text)
        self.__bot.send_message(chat_id, 'Название директории обновлено!')

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                              BotTypes.DIRS_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_dir_name(self, message: Message):
        text = message.text
        chat_id = message.chat.id

        if text in BotTypes.get_reply_commands_list():
            self.__bot.send_message(chat_id, 'Некорректное название для директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)

        elif len(text) >= 30:
            self.__bot.send_message(chat_id, 'Слишком длинное название, используйте название короче 30 символов')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name)

        elif self.__dir_controller.is_directory_in_cur_parent_exists(chat_id, text):
            self.__bot.send_message(chat_id, 'Директория с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)
        else:
            cur_dir = self.__dir_controller.get_current_directory(chat_id)
            self.__dir_controller.create_directory(text, chat_id, cur_dir.id)
            self.__bot.send_message(chat_id, 'Директория создана!')

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE, 0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_note_name(self, message: Message):
        text = message.text
        chat_id = message.chat.id

        if text in BotTypes.get_reply_commands_list():
            self.__bot.send_message(chat_id, 'Некорректное название для заметки')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)

        elif len(text) >= 30:
            self.__bot.send_message(chat_id, 'Слишком длинное название, используйте название короче 30 символов')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name)

        if self.__note_controller.is_node_in_cur_directory_exists(chat_id, text):
            self.__bot.send_message(chat_id, 'Записка с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name)
        else:
            self.__bot.send_message(chat_id, 'Введите содержимое заметки')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_content, text)

    def __handle_note_content(self, message: Message, note_name):
        content = message.text
        chat_id = message.chat.id
        cur_dir = self.__dir_controller.get_current_directory(chat_id)

        self.__note_controller.create_note(chat_id, cur_dir.id, note_name, content)
        self.__bot.send_message(chat_id, 'Записка создана!')

        text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                              BotTypes.NOTES_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __delete_directory(self, chat_id):
        cur_dir: Directory = self.__dir_controller.get_current_directory(chat_id)

        self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)
        self.__dir_controller.delete_directory(cur_dir)
        self.__bot.send_message(chat_id, 'Директория удалена')

        text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.parent_dir_id,
                                                                              BotTypes.DIRS_STORAGE_TYPE,
                                                                              0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)
