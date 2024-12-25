import json
from cache3 import SafeCache
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup


class InlineKeyboards:
    def start(self) -> InlineKeyboardMarkup:
        """  """
        
        pass
    
    def back(self) -> InlineKeyboardMarkup:
        """  """
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Назад в меню', callback_data='back_in_menu')
                ]
            ]
        )
        
        return keyboard