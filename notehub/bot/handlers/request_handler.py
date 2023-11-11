import telebot
from telebot import types
from telebot.types import Message, CallbackQuery
from bot.controllers.auth_controller import AuthController
from bot.controllers.dir_controller import DirectoryController
from bot.controllers.note_controller import NoteController
from bot.models.directory import Directory

hello_message = ('Привет! Это бот NoteHub, и он предназначен для хранения твоих заметок!\n'
                 'Сейчас будет создана твоя первая директория, где ты сможешь создавать свои заметки, '
                 'а также директории, используя кнопки под сообщением')

# STORAGE TYPES
DIRS_STORAGE_TYPE = 'dirs'
NOTES_STORAGE_TYPE = 'notes'

# NAVIGATION TYPES
BACK_MOVE_TYPE = 'back'
NEXT_PAGE_TYPE = 'next_page'
PREV_PAGE_TYPE = 'prev_page'

# BUTTON TEXTS TYPES
DELETE_BUTTON_TEXT = 'Удалить'
CREATE_DIR_BUTTON_TEXT = 'Создать директорию'
CREATE_NOTE_BUTTON_TEXT = 'Создать записку'

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

            self.__bot.send_message(chat_id, hello_message, reply_markup=_create_reply_keyboard())
            self.__auth_controller.create_user(chat_id)
            dir = self.__create_directory(message, '/', None)

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
                self.__bot.send_message(chat_id, 'Директории/записки под этим номером не существует')
                return

            dir_id = int(call_data_split[1])
            self.__dir_controller.change_current_directory(chat_id, dir_id)

            text, keyboard = self.__collect_storage_message(chat_id, dir_id, DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BACK_MOVE_TYPE))
        def handle_back_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            cur_dir: Directory = self.__dir_controller.get_current_directory(chat_id)
            if cur_dir.parent_dir_id is None:
                self.__bot.send_message(chat_id, 'Родительской директории не существует')
                return

            self.__dir_controller.change_current_directory(chat_id, cur_dir.parent_dir_id)

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.parent_dir_id, DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):
            chat_id = message.chat.id

            if message.text == DELETE_BUTTON_TEXT:
                self.__delete_directory(chat_id)

            elif message.text == CREATE_DIR_BUTTON_TEXT:
                msg = self.__bot.send_message(chat_id, 'Введите название директории:')
                self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name, [msg])

    def __handle_dir_name(self, message: Message, prev_msgs: [Message]):
        text = message.text
        chat_id = message.chat.id

        if text == CANCEL:
            self.__clear_messages(chat_id, prev_msgs)

        elif self.__dir_controller.is_directory_in_parent_exists(chat_id, text):
            msg = self.__bot.send_message(chat_id, 'Директория с таким названием уже существует в текущей директории')
            self.__bot.register_next_step_handler_by_chat_id(chat_id, self.__handle_dir_name, [*prev_msgs, msg])
        else:
            cur_dir = self.__dir_controller.get_current_directory(chat_id)
            self.__dir_controller.create_directory(text, chat_id, cur_dir.id)
            self.__bot.send_message(chat_id, 'Директория создана!')

            text, keyboard = self.__collect_storage_message(chat_id, cur_dir.id, DIRS_STORAGE_TYPE, 0)
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

        elements = self.__dir_controller.get_child_directories(chat_id, parent_dir_id)

        return _create_storage_message_with_keyboard(parent_dir, storage_type, elements, page)

    def __create_directory(self, message, name, parent_dir_id):
        dir = self.__dir_controller.create_directory(name, message.chat.id, parent_dir_id)

        if not dir:
            self.__bot.send_message(message.chat.id, 'Директория с таким названием уже существует ;(')
        else:
            self.__bot.send_message(message.chat.id, 'Директория успешно создана!')

        return dir

    def __clear_messages(self, chat_id, messages: [Message]):
        for msg in messages:
            self.__bot.delete_message(chat_id, msg.message_id)


def _create_reply_keyboard():
    keyboard = types.ReplyKeyboardMarkup()

    delete_button = types.KeyboardButton(DELETE_BUTTON_TEXT)
    create_dir_button = types.KeyboardButton(CREATE_DIR_BUTTON_TEXT)
    create_note_button = types.KeyboardButton(CREATE_NOTE_BUTTON_TEXT)

    keyboard.row(delete_button)
    keyboard.row(create_note_button, create_dir_button)

    return keyboard


def _create_store_keyboard(storage_type, elements):
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
            row2[i-3].callback_data += f'_{element.id}'
        else:
            row3[i-6].callback_data += f'_{element.id}'

    pages_row = [
        types.InlineKeyboardButton("<<", callback_data="prev_page"),
        types.InlineKeyboardButton(">>", callback_data="next_page")
    ]

    back_button = types.InlineKeyboardButton('Назад', callback_data=BACK_MOVE_TYPE)
    keyboard.add(*row1)
    keyboard.add(*row2)
    keyboard.add(*row3)
    keyboard.add(*pages_row)
    keyboard.add(back_button)

    return keyboard


def _create_storage_message_with_keyboard(parent_dir: Directory, storage_type, elements, page):
    """:param page номер страницы хранилища"""

    title = f'{parent_dir.name}'
    if not elements:
        storage_name = 'Директория пуста'
    else:
        storage_name = f'----------------DIRS----------------' if storage_type == DIRS_STORAGE_TYPE else 'Записки:'

    start_index = page * 10
    end_index = min(start_index + 10, len(elements))

    sub_elements = elements[start_index:end_index]

    message_text = title + '\n' + storage_name + '\n\n'
    for i, element in enumerate(sub_elements, start=start_index + 1):
        message_text += f'{i}. {element.name}\n'

    keyboard = _create_store_keyboard(storage_type, sub_elements)

    return message_text, keyboard
