import sys

from bot.controllers.dir_controller import DirectoryController
from bot.controllers.keyboard_controller import KeyboardController
from bot.controllers.note_controller import NoteController
from bot.models.bot_types import BotTypes
from bot.models.entities.storage import Storage


class StorageMessageCollector:

    def __init__(self, dir_controller: DirectoryController, note_controller: NoteController):
        self.__dir_controller = dir_controller
        self.__note_controller = note_controller

    def collect_storage_message(self, chat_id, parent_dir_id, storage_type, page):

        parent_dir = self.__dir_controller.get_directory(parent_dir_id)

        if not parent_dir:
            return "Error"
        elements: [Storage]

        if storage_type == BotTypes.DIRS_STORAGE_TYPE:
            elements = self.__dir_controller.get_child_directories(chat_id, parent_dir_id)
        elif storage_type == BotTypes.NOTES_STORAGE_TYPE:
            elements = self.__note_controller.get_notes_in_directory(chat_id, parent_dir_id)
        else:
            print('Error while checking storage type', file=sys.stderr)
            return

        return KeyboardController.create_storage_message_with_keyboard(parent_dir, storage_type, elements, page)
