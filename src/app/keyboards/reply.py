import json
from cache3 import SafeCache
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyKeyboards:
    def example_generate(self):
        
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Сгенерировать пример')
                ],
            ],
            resize_keyboard=True
        )
        
        return kb