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
        @self.__bot.inline_handler(func=lambda query: len(query.query) > 0)
        def query_text(query):
            digits_pattern = re.compile(r'^[0-9]+ [0-9]+$', re.MULTILINE)
            try:
                matches = re.match(digits_pattern, query.query)
            except AttributeError as ex:
                return
            num1, num2 = matches.group().split()
            try:
                m_sum = int(num1) + int(num2)
                r_sum = InlineQueryResultArticle(
                    id='1', title="Сумма",
                    # Описание отображается в подсказке,
                    # message_text - то, что будет отправлено в виде сообщения
                    description="Результат: {!s}".format(m_sum),
                    input_message_content=InputTextMessageContent(
                        message_text="{!s} + {!s} = {!s}".format(num1, num2, m_sum))
                )
                m_sub = int(num1) - int(num2)
                r_sub = InlineQueryResultArticle(
                    id='2', title="Разность",
                    description="Результат: {!s}".format(m_sub),
                    input_message_content=InputTextMessageContent(
                        message_text="{!s} - {!s} = {!s}".format(num1, num2, m_sub))
                )
                # Учтем деление на ноль и подготовим 2 варианта развития событий
                if num2 is not "0":
                    m_div = int(num1) / int(num2)
                    r_div = InlineQueryResultArticle(
                        id='3', title="Частное",
                        description="Результат: {0:.2f}".format(m_div),
                        input_message_content=InputTextMessageContent(
                            message_text="{0!s} / {1!s} = {2:.2f}".format(num1, num2, m_div))
                    )
                else:
                    r_div = InlineQueryResultArticle(
                        id='3', title="Частное", description="На ноль делить нельзя!",
                        input_message_content=InputTextMessageContent(
                            message_text="Я нехороший человек и делю на ноль!")
                    )
                m_mul = int(num1) * int(num2)
                r_mul = InlineQueryResultArticle(
                    id='4', title="Произведение",
                    description="Результат: {!s}".format(m_mul),
                    input_message_content=InputTextMessageContent(
                        message_text="{!s} * {!s} = {!s}".format(num1, num2, m_mul))
                )
                self.__bot.answer_inline_query(query.id, [r_sum, r_sub, r_div, r_mul])
            except Exception as e:
                print("{!s}\n{!s}".format(type(e), str(e)))

        @self.__bot.message_handler(func=lambda message: message.text in BotTypes.get_reply_commands_list())
        def handle_reply_buttons_message(message: Message):
            chat_id = message.chat.id

            if message.text == BotTypes.DELETE_DIR_BUTTON_TEXT:
                self.__delete_directory(chat_id)

            elif message.text == BotTypes.CREATE_DIR_BUTTON_TEXT:
                msg = self.__bot.send_message(chat_id, 'Введите название директории:')
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
        new_name = message.text

        self.__dir_controller.rename_directory(dir_id, new_name)
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
        if cur_dir.parent_dir_id is None:
            self.__bot.send_message(chat_id, 'Корневую директорию нельзя удалить')
        else:
            self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)
            self.__dir_controller.delete_directory(cur_dir)
            self.__bot.send_message(chat_id, 'Директория удалена')

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.parent_dir_id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE,
                                                                                  0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)
