import sys

import telebot
from telebot import types
from telebot.types import Message, CallbackQuery
from bot.controllers.auth_controller import AuthController
from bot.controllers.dir_controller import DirectoryController
from bot.controllers.note_controller import NoteController
from bot.models.directory import Directory
from bot.models.storage import Storage

hello_message = ('Привет! Это бот NoteHub, и он предназначен для хранения твоих заметок!\n'
                 'Сейчас будет создана твоя первая директория, где ты сможешь создавать свои заметки, '
                 'а также директории, используя кнопки под сообщением')

# STORAGE TYPES
DIRS_STORAGE_TYPE = 'dirs'
NOTES_STORAGE_TYPE = 'notes'

# STORAGE NAVIGATION TYPES
BACK_MOVE_TYPE = 'back'
NEXT_PAGE_TYPE = 'next'
PREV_PAGE_TYPE = 'prev'
PREV_EMPTY = -1
NEXT_EMPTY = -2

# NOTE OPERATIONS TYPES
DELETE_NOTE_TYPE = 'del'
RENAME_NOTE_TYPE = 'rename'
CHANGE_NOTE_CONTENT_TYPE = 'changecontent'

# BUTTON TEXTS TYPES
DELETE_DIR_BUTTON_TEXT = 'Удалить директорию'
DELETE_NOTE_BUTTON_TEXT = 'Удалить заметку'
RENAME_DIR_BUTTON_TEXT = 'Изменить название директории'
RENAME_NOTE_BUTTON_TEXT = 'Изменить название заметки'
CHANGE_NOTE_CONTENT_BUTTON_TEXT = 'Изменить содержимое'
CREATE_DIR_BUTTON_TEXT = 'Создать директорию'
CREATE_NOTE_BUTTON_TEXT = 'Создать заметку'
CHANGE_TO_DIRS_BUTTON_TEXT = 'Показать директории'
CHANGE_TO_NOTES_BUTTON_TEXT = 'Показать заметки'

# OPTIONAL BUTTON TEXT
CANCEL = 'Отмена'


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
            # if self.__auth_controller.get_user(message.from_user.id):
            #     return
            chat_id = message.chat.id

            self.__bot.send_message(chat_id, hello_message,
                                    reply_markup=_create_directory_reply_keyboard(DIRS_STORAGE_TYPE))
            self.__auth_controller.create_user(chat_id)
            dir = self.__dir_controller.create_root(chat_id)

            if not dir:
                dir = self.__dir_controller.get_root_directory(chat_id)

            self.__dir_controller.create_user_current_directory(chat_id, dir.id)

            text, keyboard = self.__collect_storage_message(chat_id, dir.id, DIRS_STORAGE_TYPE, 0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(DIRS_STORAGE_TYPE))
        def handle_dir_show_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 2:
                self.__bot.send_message(chat_id, 'Директории под этим номером не существует')
                return

            dir_id = int(call_data_split[1])
            self.__dir_controller.change_current_directory(chat_id, dir_id)

            text, keyboard = self.__collect_storage_message(chat_id, dir_id, DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(NOTES_STORAGE_TYPE))
        def handle_note_show_callback_handler(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 2:
                self.__bot.send_message(chat_id, 'Заметки под этим номером не существует')
                return

            note_id = int(call_data_split[1])
            note = self.__note_controller.get_note(note_id)
            keyboard = self.__create_note_inline_keyboard(note_id)

            self.__bot.send_message(chat_id, f'Название: {note.get_name()}\nТекст:\n{note.content}',
                                    reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BACK_MOVE_TYPE))
        def handle_back_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            cur_dir: Directory = self.__dir_controller.get_current_directory(chat_id)
            if cur_dir.parent_dir_id is None:
                self.__bot.send_message(chat_id, 'Родительской директории не существует')
                return

            self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.parent_dir_id, DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(NEXT_PAGE_TYPE) or
                                                             call.data.startswith(PREV_PAGE_TYPE))
        def handle_page_move_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            data = call.data.split('_')
            page = int(data[1])

            if page == PREV_EMPTY:
                self.__bot.send_message(chat_id, 'Предыдущей страницы нет')
                return
            elif page == NEXT_EMPTY:
                self.__bot.send_message(chat_id, 'Следующей страницы нет')
                return

            cur_dir = self.__dir_controller.get_current_directory(chat_id)

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, DIRS_STORAGE_TYPE, page)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(CHANGE_NOTE_CONTENT_TYPE) or
                                                             call.data.startswith(RENAME_NOTE_TYPE) or
                                                             call.data.startswith(DELETE_NOTE_TYPE))
        def handle_note_operations_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            data = call.data.split('_')
            note_id = int(data[1])

            if data[0] == CHANGE_NOTE_CONTENT_TYPE:
                self.__bot.send_message(chat_id, 'Введите новый текст заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_content_change, note_id)
            elif data[0] == RENAME_NOTE_TYPE:
                self.__bot.send_message(chat_id, 'Введите новое название для заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_note, note_id)
            elif data[0] == DELETE_NOTE_TYPE:
                self.__note_controller.delete_note(note_id)
                self.__bot.send_message(chat_id, 'Заметка удалена')

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, NOTES_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

        @self.__bot.message_handler(func=lambda message: True)
        def handle_reply_buttons_message(message: Message):
            chat_id = message.chat.id

            if message.text == DELETE_DIR_BUTTON_TEXT:
                self.__delete_directory(chat_id)

            elif message.text == CREATE_DIR_BUTTON_TEXT:
                msg = self.__bot.send_message(chat_id, 'Введите название директории:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name, [message, msg])

            elif message.text == CHANGE_TO_NOTES_BUTTON_TEXT:
                reply_keyboard = _create_directory_reply_keyboard(NOTES_STORAGE_TYPE)
                self.__bot.send_message(chat_id, 'Вы сменили показ на заметки', reply_markup=reply_keyboard)

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, NOTES_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id, text, reply_markup=keyboard)

            elif message.text == CHANGE_TO_DIRS_BUTTON_TEXT:
                reply_keyboard = _create_directory_reply_keyboard(DIRS_STORAGE_TYPE)
                self.__bot.send_message(chat_id, 'Вы сменили показ на директории', reply_markup=reply_keyboard)

                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, DIRS_STORAGE_TYPE, 0)
                self.__bot.send_message(chat_id, text, reply_markup=keyboard)

            elif message.text == CREATE_NOTE_BUTTON_TEXT:
                msg = self.__bot.send_message(chat_id, 'Введите название заметки:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name, [message, msg])

            elif message.text == RENAME_DIR_BUTTON_TEXT:
                self.__bot.send_message(chat_id, 'Введите название директории:')
                cur_dir = self.__dir_controller.get_current_directory(chat_id)
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_rename_directory, cur_dir.id)

    def __handle_rename_directory(self, message: Message, dir_id):
        chat_id = message.chat.id
        new_name = message.text

        self.__dir_controller.rename_directory(dir_id, new_name)
        self.__bot.send_message(chat_id, 'Название директории обновлено!')

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, DIRS_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_rename_note(self, message: Message, note_id):
        chat_id = message.chat.id
        new_name = message.text

        self.__note_controller.rename_note(note_id, new_name)
        self.__bot.send_message(chat_id, 'Название заметки обновлено!')

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, NOTES_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_content_change(self, message: Message, note_id):
        chat_id = message.chat.id
        new_content = message.text

        self.__note_controller.update_note_content(note_id, new_content)
        self.__bot.send_message(chat_id, 'Содержимое заметки обновлено!')

        cur_dir = self.__dir_controller.get_current_directory(chat_id)
        text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, NOTES_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_dir_name(self, message: Message, prev_msgs: [Message]):
        text = message.text
        chat_id = message.chat.id

        if text.lower() == CANCEL.lower():
            self.__clear_messages(chat_id, [message, *prev_msgs])

        elif self.__dir_controller.is_directory_in_cur_parent_exists(chat_id, text):
            msg = self.__bot.send_message(chat_id, 'Директория с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name,
                                                             [*prev_msgs, msg, message])
        else:
            cur_dir = self.__dir_controller.get_current_directory(chat_id)
            self.__dir_controller.create_directory(text, chat_id, cur_dir.id)
            self.__bot.send_message(chat_id, 'Директория создана!')

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, DIRS_STORAGE_TYPE, 0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __handle_note_name(self, message: Message, prev_msgs: [Message]):
        text = message.text
        chat_id = message.chat.id

        if text.lower() == CANCEL.lower():
            self.__clear_messages(chat_id, prev_msgs)

        elif self.__note_controller.is_node_in_cur_directory_exists(chat_id, text):
            msg = self.__bot.send_message(chat_id, 'Записка с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_name, [*prev_msgs, msg])
        else:
            self.__bot.send_message(chat_id, 'Введите содержимое заметки')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_note_content, text)

    def __handle_note_content(self, message: Message, note_name):
        content = message.text
        chat_id = message.chat.id
        cur_dir = self.__dir_controller.get_current_directory(chat_id)

        self.__note_controller.create_note(chat_id, cur_dir.id, note_name, content)
        self.__bot.send_message(chat_id, 'Записка создана!')

        text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, NOTES_STORAGE_TYPE, 0)
        self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __delete_directory(self, chat_id):
        cur_dir: Directory = self.__dir_controller.get_current_directory(chat_id)
        if cur_dir.parent_dir_id is None:
            self.__bot.send_message(chat_id, 'Корневую директорию нельзя удалить')
        else:
            self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)
            self.__dir_controller.delete_directory(cur_dir)
            self.__bot.send_message(chat_id, 'Директория удалена')

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.parent_dir_id, DIRS_STORAGE_TYPE,
                                                            0)
            self.__bot.send_message(chat_id, text, reply_markup=keyboard)

    def __collect_storage_message(self, chat_id, parent_dir_id, storage_type, page):

        parent_dir = self.__dir_controller.get_directory(parent_dir_id)

        if not parent_dir:
            return "Error"
        elements: [Storage]

        if storage_type == DIRS_STORAGE_TYPE:
            elements = self.__dir_controller.get_child_directories(chat_id, parent_dir_id)
        elif storage_type == NOTES_STORAGE_TYPE:
            elements = self.__note_controller.get_notes_in_directory(chat_id, parent_dir_id)
        else:
            print('Error while checking storage type', file=sys.stderr)
            return

        return _create_storage_message_with_keyboard(parent_dir, storage_type, elements, page)

    def __create_directory(self, message, name, parent_dir_id):
        dir = self.__dir_controller.create_directory(name, message.chat.id, parent_dir_id)

        if not dir:
            self.__bot.send_message(message.chat.id, 'Директория с таким названием уже существует ;(')
        else:
            self.__bot.send_message(message.chat.id, 'Директория успешно создана!')

        return dir

    def __create_note_inline_keyboard(self, note_id):
        keyboard = types.InlineKeyboardMarkup()

        delete_button = types.InlineKeyboardButton(DELETE_NOTE_BUTTON_TEXT,
                                                   callback_data=DELETE_NOTE_TYPE + "_" + str(note_id))
        change_name_button = types.InlineKeyboardButton(RENAME_NOTE_BUTTON_TEXT,
                                                        callback_data=RENAME_NOTE_TYPE + "_" + str(note_id))
        change_content_button = types.InlineKeyboardButton(CHANGE_NOTE_CONTENT_BUTTON_TEXT,
                                                           callback_data=CHANGE_NOTE_CONTENT_TYPE + "_" + str(note_id))

        keyboard.row(delete_button, change_name_button, change_content_button)

        return keyboard

    def __clear_messages(self, chat_id, messages: [Message]):
        for msg in messages:
            self.__bot.delete_message(chat_id, msg.message_id)


def _create_directory_reply_keyboard(storage_type):
    keyboard = types.ReplyKeyboardMarkup()

    delete_button = types.KeyboardButton(DELETE_DIR_BUTTON_TEXT)
    change_name_button = types.KeyboardButton(RENAME_DIR_BUTTON_TEXT)

    create_dir_button = types.KeyboardButton(CREATE_DIR_BUTTON_TEXT)
    create_note_button = types.KeyboardButton(CREATE_NOTE_BUTTON_TEXT)

    change_to_storage_button = types.KeyboardButton(
        CHANGE_TO_DIRS_BUTTON_TEXT if storage_type == NOTES_STORAGE_TYPE else CHANGE_TO_NOTES_BUTTON_TEXT)

    keyboard.row(create_note_button, create_dir_button)
    keyboard.row(change_to_storage_button)
    keyboard.row(delete_button, change_name_button)

    return keyboard


def _create_store_keyboard(storage_type, elements, page, is_last_page):
    """:param storage_type тип хранилища, для которого формируется клавиатура (dirs, notes)"""

    keyboard = types.InlineKeyboardMarkup()

    row1 = [types.InlineKeyboardButton(str(i), callback_data=f"{storage_type}") for i in
            range(1, 4)]
    row2 = [types.InlineKeyboardButton(str(i), callback_data=f"{storage_type}") for i in
            range(4, 7)]
    row3 = [types.InlineKeyboardButton(str(i), callback_data=f"{storage_type}") for i in
            range(7, 10)]

    for i, element in enumerate(elements):
        if i < 3:
            row1[i].callback_data += f'_{element.id}'
        elif i < 6:
            row2[i - 3].callback_data += f'_{element.id}'
        else:
            row3[i - 6].callback_data += f'_{element.id}'

    pages_row = [
        types.InlineKeyboardButton("<<",
                                   callback_data=PREV_PAGE_TYPE + '_' + str(page - 1 if page != 0 else PREV_EMPTY)),
        types.InlineKeyboardButton(">>",
                                   callback_data=NEXT_PAGE_TYPE + '_' + str(NEXT_EMPTY if is_last_page else page + 1))
    ]

    back_button = types.InlineKeyboardButton('Назад', callback_data=BACK_MOVE_TYPE)

    keyboard.add(*row1)
    keyboard.add(*row2)
    keyboard.add(*row3)
    keyboard.add(*pages_row)

    keyboard.add(back_button)

    return keyboard


def _create_storage_message_with_keyboard(parent_dir: Directory, storage_type, elements: [Storage], page):
    """:param page номер страницы хранилища"""

    title = f'{parent_dir.name}'
    page_title = f'Страница {page + 1}'
    if not elements:
        if storage_type == DIRS_STORAGE_TYPE:
            storage_name = 'Директория пуста'
        elif storage_type == NOTES_STORAGE_TYPE:
            storage_name = 'Записок нет'
        else:
            print(f'Error while match storage name', file=sys.stderr)
            storage_name = ''
    else:
        if storage_type == DIRS_STORAGE_TYPE:
            storage_name = '----------------DIRS----------------'
        elif storage_type == NOTES_STORAGE_TYPE:
            storage_name = '----------------NOTES----------------'
        else:
            print(f'Error while match storage name', file=sys.stderr)
            storage_name = ''

    start_index = page * 10 - (0 if page == 0 else 1)
    end_index = min(start_index + 9, len(elements))

    sub_elements = elements[start_index:end_index]

    message_text = title + '\n' + page_title + '\n' + storage_name + '\n\n'
    for i, element in enumerate(sub_elements, start=start_index + 1):
        message_text += f'{i}. {element.get_name()}\n'

    keyboard = _create_store_keyboard(storage_type, sub_elements, page, len(elements) == end_index)

    return message_text, keyboard
