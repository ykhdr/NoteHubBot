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

# MOVES TYPES
BACK_MOVE_TYPE = 'back'


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

            self.__bot.send_message(message.chat.id, hello_message)
            self.__auth_controller.create_user(message.chat.id)
            dir = self.__create_directory(message, '/', None)

            if not dir:
                dir = self.__dir_controller.get_directory(1)

            text, keyboard = self.__collect_storage_message(message, dir.id, DIRS_STORAGE_TYPE, 0)
            self.__bot.send_message(message.chat.id, text, reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(DIRS_STORAGE_TYPE))
        def handle_dirs_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 3:
                self.__bot.send_message(chat_id, 'Директории/записки под этим номером не существует')
                return

            parent_dir_id = int(call_data_split[1])
            page = int(call_data_split[2])

            text, keyboard = self.__collect_storage_message(call.message, parent_dir_id, DIRS_STORAGE_TYPE, page)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith(BACK_MOVE_TYPE))
        def handle_back_callback_query(call: CallbackQuery):
            chat_id = call.message.chat.id

            call_data_split = call.data.split('_')
            if len(call_data_split) < 2 or call_data_split[1] == 'None':
                self.__bot.send_message(chat_id, 'Родительской директории не существует')
                return

            parent_dir_id = int(call_data_split[1])

            text, keyboard = self.__collect_storage_message(call.message, parent_dir_id, DIRS_STORAGE_TYPE, 0)
            self.__bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text,
                                         reply_markup=keyboard)

        @self.__bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):
            self.__bot.reply_to(message, message.text)

    def __collect_storage_message(self, message, parent_dir_id, storage_type, page):

        parent_dir = self.__dir_controller.get_directory(parent_dir_id)

        if not parent_dir:
            return "Error"

        elements = self.__dir_controller.get_child_directories(message.chat.id, parent_dir_id)

        return _create_storage_message_with_keyboard(parent_dir, storage_type, elements, page)

    def __create_directory(self, message, name, parent_dir):
        dir = self.__dir_controller.create_directory(name, message.chat.id, parent_dir)

        if not dir:
            self.__bot.send_message(message.chat.id, 'Директория с таким названием уже существует ;(')
        else:
            self.__bot.send_message(message.chat.id, 'Директория успешно создана!')

        return dir


def _create_keyboard(storage_type, parent_dir, elements, page):
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
            row1[i].callback_data += f'_{element.id}_{page}'
        elif i < 6:
            row2[i].callback_data += f'_{element.id}_{page}'
        else:
            row3[i].callback_data += f'_{element.id}_{page}'

    pages_row = [
        types.InlineKeyboardButton("<<", callback_data="prev_page"),
        types.InlineKeyboardButton(">>", callback_data="next_page")
    ]

    back_button = types.InlineKeyboardButton('Назад', callback_data=f'back_{parent_dir.parent_dir_id}')
    keyboard.add(*row1)
    keyboard.add(*row2)
    keyboard.add(*row3)
    keyboard.add(*pages_row)
    keyboard.add(back_button)

    return keyboard


def _create_storage_message_with_keyboard(parent_dir: Directory, storage_type, elements, page):
    """:param page номер страницы хранилища"""

    title = f' Директория {parent_dir.name}'
    if not elements:
        storage_name = 'Директория пуста'
    else:
        storage_name = f'Директории:' if storage_type == DIRS_STORAGE_TYPE else 'Записки:'

    start_index = page * 10
    end_index = min(start_index + 10, len(elements))

    sub_elements = elements[start_index:end_index]

    message_text = title + '\n' + storage_name + '\n\n'
    for i, element in enumerate(sub_elements, start=start_index + 1):
        message_text += f'{i}. {element.name}\n'

    keyboard = _create_keyboard(storage_type, parent_dir, sub_elements, page)

    return message_text, keyboard
