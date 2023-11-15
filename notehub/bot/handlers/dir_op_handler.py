from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.controllers.dir_controller import DirectoryController
from bot.controllers.note_controller import NoteController
from bot.controllers.storage_msg_collector import StorageMessageCollector
from bot.handlers.handler import Handler
from bot.models.bot_types import BotTypes
from bot.models.entities.directory import Directory


class DirectoryOperationsHandler(Handler):
    def __init__(self, bot: TeleBot, dir_controller: DirectoryController, note_controller: NoteController,
                 storage_msg_collector: StorageMessageCollector):
        self.__bot = bot
        self.__note_controller = note_controller
        self.__dir_controller = dir_controller
        self.__storage_msg_collector = storage_msg_collector

    def setup_handler(self):
        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.DIRS_STORAGE_TYPE))
        def handle_dir_show_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 2:
                self.__bot.answer_callback_query(call.id, 'Директории под этим номером не существует')
                return

            dir_id = int(call_data_split[1])
            self.__dir_controller.change_current_directory(chat_id, dir_id)

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, dir_id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

            self.__bot.answer_callback_query(call.id)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.BACK_MOVE_TYPE))
        def handle_back_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            cur_dir: Directory = self.__dir_controller.get_current_directory(chat_id)
            if cur_dir.parent_dir_id is None:
                self.__bot.answer_callback_query(call.id, 'Родительской директории не существует')
                return

            self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.parent_dir_id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE,
                                                                                  0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                         reply_markup=keyboard)

            self.__bot.answer_callback_query(call.id)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.NEXT_PAGE_TYPE) or
                                                             call.data.startswith(BotTypes.PREV_PAGE_TYPE))
        def handle_page_move_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            data = call.data.split('_')
            page = int(data[1])

            if page == BotTypes.PREV_EMPTY:
                self.__bot.answer_callback_query(call.id, 'Предыдущей страницы нет')
                return
            elif page == BotTypes.NEXT_EMPTY:
                self.__bot.answer_callback_query(call.id, 'Следующей страницы нет')
                return

            cur_dir = self.__dir_controller.get_current_directory(chat_id)

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                  BotTypes.DIRS_STORAGE_TYPE, page)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                         reply_markup=keyboard)

            self.__bot.answer_callback_query(call.id)
