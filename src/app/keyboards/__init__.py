from app.keyboards import inline, reply


class Keyboards:
    def __init__(self):
        self.inline = inline.InlineKeyboards()
        self.reply = reply.ReplyKeyboards()
    

keyboards = Keyboards()

__all__ = (
    'keyboards',
)