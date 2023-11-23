import telebot
from telebot.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.controllers.note_controller import NoteController
from bot.handlers.handler import Handler
from bot.models.entities.note import Note


class NoteShareInlineHandler(Handler):
    def __init__(self, bot: telebot.TeleBot, note_controller: NoteController):
        self.__bot = bot
        self.__note_controller = note_controller

    def setup_handler(self):
        @self.__bot.inline_handler(func=lambda query: len(query.query) > 0)
        def handle_note_share(query: InlineQuery):
            query_id = query.id
            user_id = query.from_user.id
            text = query.query

            notes = self.__note_controller.get_user_notes_like(user_id, text)
            if not notes:
                res = InlineQueryResultArticle(id=1,
                                               title=f'Нет записок c таким названием',
                                               input_message_content=InputTextMessageContent('Нет такой записки :('))
                self.__bot.answer_inline_query(query_id, [res])

            else:
                res: [InlineQueryResultArticle] = []
                for i, note in enumerate(notes):
                    path = NoteShareInlineHandler._get_path(note)
                    res.append(InlineQueryResultArticle(id=i,
                                                        title=f'{path}',
                                                        description=f'{note.content[:20]}',
                                                        input_message_content=InputTextMessageContent(
                                                            f'{note.content}')))
                self.__bot.answer_inline_query(query_id, res)

    @staticmethod
    def _get_path(note: Note):
        path = '' if note.dir.name == '/' else note.dir.name

        return f'{path}/{note.name}'
