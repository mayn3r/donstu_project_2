from aiogram import Router, F#, types, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """ /start """
    
    await message.answer("Добро пожаловать!")