import sys

from telebot import types

from bot.models.bot_types import BotTypes
from bot.models.entities.directory import Directory
from bot.models.entities.storage import Storage


class KeyboardController:

    @staticmethod
    def create_note_inline_keyboard(note_id):
        keyboard = types.InlineKeyboardMarkup()

        delete_button = types.InlineKeyboardButton(BotTypes.DELETE_NOTE_BUTTON_TEXT,
                                                   callback_data=BotTypes.DELETE_NOTE_TYPE + "_" + str(note_id))
        change_name_button = types.InlineKeyboardButton(BotTypes.RENAME_NOTE_BUTTON_TEXT,
                                                        callback_data=BotTypes.RENAME_NOTE_TYPE + "_" + str(note_id))
        change_content_button = types.InlineKeyboardButton(BotTypes.CHANGE_NOTE_CONTENT_BUTTON_TEXT,
                                                           callback_data=BotTypes.CHANGE_NOTE_CONTENT_TYPE + "_" + str(
                                                               note_id))

        keyboard.row(delete_button, change_name_button, change_content_button)

        return keyboard

    @staticmethod
    def create_note_delete_confirm_keyboard(note_id):
        keyboard = types.InlineKeyboardMarkup()

        confirm = types.InlineKeyboardButton(BotTypes.CONFIRM_DELETE,
                                             callback_data=BotTypes.CONFIRM_DELETE + '_' + str(note_id))
        cancel = types.InlineKeyboardButton(BotTypes.CANCEL, callback_data=BotTypes.CANCEL)

        keyboard.row(cancel, confirm)

        return keyboard

    @staticmethod
    def create_directory_reply_keyboard(storage_type):
        keyboard = types.ReplyKeyboardMarkup()

        delete_button = types.KeyboardButton(BotTypes.DELETE_DIR_BUTTON_TEXT)
        change_name_button = types.KeyboardButton(BotTypes.RENAME_DIR_BUTTON_TEXT)

        create_dir_button = types.KeyboardButton(BotTypes.CREATE_DIR_BUTTON_TEXT)
        create_note_button = types.KeyboardButton(BotTypes.CREATE_NOTE_BUTTON_TEXT)

        change_to_storage_button = types.KeyboardButton(
            BotTypes.CHANGE_TO_DIRS_BUTTON_TEXT if storage_type == BotTypes.NOTES_STORAGE_TYPE else BotTypes.CHANGE_TO_NOTES_BUTTON_TEXT)

        keyboard.row(create_note_button, create_dir_button)
        keyboard.row(change_to_storage_button)
        keyboard.row(delete_button, change_name_button)

        return keyboard

    @staticmethod
    def create_store_keyboard(storage_type, elements, page, is_last_page):
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
                                       callback_data=BotTypes.PREV_PAGE_TYPE + '_' + str(
                                           page - 1 if page != 0 else BotTypes.PREV_EMPTY)),
            types.InlineKeyboardButton(">>",
                                       callback_data=BotTypes.NEXT_PAGE_TYPE + '_' + str(
                                           BotTypes.NEXT_EMPTY if is_last_page else page + 1))
        ]

        back_button = types.InlineKeyboardButton('Назад', callback_data=BotTypes.BACK_MOVE_TYPE)

        keyboard.add(*row1)
        keyboard.add(*row2)
        keyboard.add(*row3)
        keyboard.add(*pages_row)

        keyboard.add(back_button)

        return keyboard

    @staticmethod
    def create_storage_message_with_keyboard(parent_dir: Directory, storage_type, elements: [Storage], page):

        title = f'{parent_dir.name}'
        page_title = f'Страница {page + 1}'
        if not elements:
            if storage_type == BotTypes.DIRS_STORAGE_TYPE:
                storage_name = 'Директория пуста'
            elif storage_type == BotTypes.NOTES_STORAGE_TYPE:
                storage_name = 'Записок нет'
            else:
                print(f'Error while match storage name', file=sys.stderr)
                storage_name = ''
        else:
            if storage_type == BotTypes.DIRS_STORAGE_TYPE:
                storage_name = '----------------DIRS----------------'
            elif storage_type == BotTypes.NOTES_STORAGE_TYPE:
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

        keyboard = KeyboardController.create_store_keyboard(storage_type, sub_elements, page,
                                                            len(elements) == end_index)

        return message_text, keyboard
