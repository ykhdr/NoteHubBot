class BotTypes:
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

    # NOTE DELETE CONFIRMATION
    CANCEL = 'Отмена'
    CONFIRM_DELETE = 'Да'

    @staticmethod
    def get_reply_commands_list():
        return [BotTypes.DELETE_DIR_BUTTON_TEXT,
                BotTypes.CREATE_DIR_BUTTON_TEXT,
                BotTypes.CHANGE_TO_NOTES_BUTTON_TEXT,
                BotTypes.CHANGE_TO_DIRS_BUTTON_TEXT,
                BotTypes.CREATE_NOTE_BUTTON_TEXT,
                BotTypes.RENAME_DIR_BUTTON_TEXT]
