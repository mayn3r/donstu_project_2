from aiogram import Router, F#, types, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup

from app.utils import ProblemGenerate
from app.models import User, ProblemModel
from app.keyboards import keyboards


class ExampleState(StatesGroup):
    model = State()
    answer  = State()
    


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """ /start """
    
    await message.answer("Добро пожаловать!\n\n/example", reply_markup=keyboards.reply.example_generate())



@router.message(F.text == 'Сгенерировать пример')
@router.message(F.text.lower() == "/example")
async def exampler_handler(message: Message, state: FSMContext, user_model: User):
    
    generate = ProblemGenerate()
    
    user_level = int(user_model.level)
    
    await message.answer(f'Ваш уровень: {user_level+1}\nИдет генерация примера...')
    
    example: dict = await generate.generate_to_while(
            level=user_level,
            img_percent=500,
            img_save_path='attachments',
            
            sleep_seconds=3
        )
    
    photo = FSInputFile(example['img']['path'])

    await message.answer_photo(photo=photo)
    await message.answer("[test] Ответ: "+(', '.join(example['answers'])))
    
    ex_model = await ProblemModel.create(
        problem=example['problem'],
        answer=','.join(example['answers']),
        filename=example['img']['filename'],
        path=example['img']['path'],
        url=example['img']['url'],
        level=user_level
    )
    
    await state.update_data(model=ex_model)
    await state.set_state(ExampleState.answer)
    

@router.message(ExampleState.answer)
async def example_answer(message: Message, state: FSMContext, user_model: User):
    """  """
    
    answer = message.text
    
    if not answer.isdigit():
        return await message.answer("Ответ должен быть целым числом")
    
    state_data: dict = await state.get_data()
    
    
    ex_model: ProblemModel = state_data['model']
    
    answers: list = ex_model.answer.split(',')
    
    if answer in answers:
        user_model.completed_tasks += 1
        
        if user_model.level == 4:
            await message.answer("Ответ верный!", reply_markup=keyboards.reply.example_generate())
            
        elif user_model.completed_tasks >= 5:
            await message.answer("Ответ верный! Ваш уровень повышен!", reply_markup=keyboards.reply.example_generate())
            
            user_model.completed_tasks = 0
            user_model.level += 1
        else:
            await message.answer('Ответ верный! Необходимо решить еще %d примеров для повышения уровня!' % (5-user_model.completed_tasks), reply_markup=keyboards.reply.example_generate())
        
        await user_model.save()
        await state.clear()
    else:
        await message.answer("Неверный ответ! Попробуйте еще раз!")