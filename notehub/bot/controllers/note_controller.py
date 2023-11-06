from bot.repositories.note_repository import NoteRepository


class NoteController:
    def __init__(self):
        self.__note_repository = NoteRepository()
