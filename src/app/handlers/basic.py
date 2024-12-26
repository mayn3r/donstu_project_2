from aiogram import Router, F#, types, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

from app.utils import ProblemGenerate
from app.models import User, ProblemModel

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """ /start """
    
    await message.answer("Добро пожаловать!\n\n/example")



@router.message(F.text.lower() == "/example")
async def exampler_handler(message: Message, user_model: User):
    
    generate = ProblemGenerate()
    
    user_level = int(user_model.level)
    
    await message.answer(f'Ваш уровень: {user_level+1}\nИдет генерация примера...')
    
    example: dict = await generate.generate_to_while(
            level=user_level,
            img_percent=500,
            img_save_path='attachments',
            
            sleep_seconds=3
        )

    print(example)
    
    photo = FSInputFile(example['img']['path'])

    await message.answer_photo(photo=photo)
    
    await ProblemModel.create(
        problem=example['problem'],
        answer=','.join(example['answers']),
        filename=example['img']['filename'],
        path=example['img']['path'],
        url=example['img']['url'],
        level=user_level
    )
    