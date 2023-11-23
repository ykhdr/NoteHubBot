from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.controllers.dir_controller import DirectoryController
from bot.controllers.keyboard_controller import KeyboardController
from bot.controllers.note_controller import NoteController
from bot.controllers.storage_msg_collector import StorageMessageCollector
from bot.handlers.handler import Handler
from bot.models.bot_types import BotTypes


class NoteOperationsHandler(Handler):

    def __init__(self, bot: TeleBot, dir_controller: DirectoryController, note_controller: NoteController,
                 storage_msg_collector: StorageMessageCollector):
        self.__bot = bot
        self.__note_controller = note_controller
        self.__dir_controller = dir_controller
        self.__storage_msg_collector = storage_msg_collector

    def setup_handler(self):
        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.CHANGE_NOTE_CONTENT_TYPE) or
                                                             call.data.startswith(BotTypes.RENAME_NOTE_TYPE) or
                                                             call.data.startswith(BotTypes.DELETE_NOTE_TYPE))
        def handle_note_operations_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            data = call.data.split('_')
            note_id = int(data[1])

            if data[0] == BotTypes.CHANGE_NOTE_CONTENT_TYPE:
                self.__bot.send_message(chat_id, 'Введите новый текст заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_content_change, note_id)
            elif data[0] == BotTypes.RENAME_NOTE_TYPE:
                self.__bot.send_message(chat_id, 'Введите новое название для заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_note, note_id)
            elif data[0] == BotTypes.DELETE_NOTE_TYPE:

                keyboard = KeyboardController.create_note_delete_confirm_keyboard(note_id)
                text = 'Вы уверены, что хотите удалить записку?'
                self.__bot.send_message(chat_id, text, reply_markup=keyboard)

            self.__bot.answer_callback_query(call.id)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.CONFIRM_DELETE) or
                                                             call.data.startswith(BotTypes.CANCEL))
        def handle_note_delete_confirmation(call: CallbackQuery):
            chat_id = call.message.chat.id

            data = call.data.split('_')

            if data[0] == BotTypes.CONFIRM_DELETE:
                note_id = int(data[1])
                self.__note_controller.delete_note(note_id)
                self.__bot.answer_callback_query(call.id, 'Заметка удалена')
                self.__bot.delete_message(chat_id, message_id=call.message.message_id)

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                      BotTypes.NOTES_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

            else:
                self.__bot.delete_message(chat_id, message_id=call.message.message_id)
                self.__bot.answer_callback_query(call.id)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BotTypes.NOTES_STORAGE_TYPE))
        def handle_note_show_callback_handler(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 2:
                self.__bot.answer_callback_query(call.id, 'Заметки под этим номером не существует')
                return

            note_id = int(call_data_split[1])
            note = self.__note_controller.get_note(note_id)
            keyboard = KeyboardController.create_note_inline_keyboard(note_id)

            self.__bot.send_message(chat_id, f'Название: {note.get_name()}\nТекст:\n{note.content}',
                                    reply_markup=keyboard)

            self.__bot.answer_callback_query(call.id)

    def __handle_rename_note(self, message: Message, note_id):
        chat_id = message.chat.id
        new_name = message.text

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        notes = self.__note_controller.get_notes_in_directory(chat_id, cur_dir.id)

        for note in notes:
            if note.name == new_name:
                self.__bot.send_message(chat_id,'Записка с таким названием уже существует в текущей директории')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_note, note_id)
                return
        if len(new_name) >= 30:
            self.__bot.send_message(chat_id, 'Слишком длинное название, используйте название короче 30 символов')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_note, note_id)

        elif new_name in BotTypes.get_reply_commands_list():
            self.__bot.send_message(chat_id, 'Некорректное название для записки')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_note, note_id)

        else:
            self.__note_controller.rename_note(note_id, new_name)
            self.__bot.send_message(chat_id, 'Название заметки обновлено!')

            cur_dir = self.__dir_controller.get_current_directory(chat_id)

            text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                                  BotTypes.NOTES_STORAGE_TYPE, 0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_content_change(self, message: Message, note_id):
        chat_id = message.chat.id
        new_content = message.text

        self.__note_controller.update_note_content(note_id, new_content)
        self.__bot.send_message(chat_id, 'Содержимое заметки обновлено!')

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        text, keyboard = self.__storage_msg_collector.collect_storage_message(chat_id, cur_dir.id,
                                                                              BotTypes.NOTES_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)
