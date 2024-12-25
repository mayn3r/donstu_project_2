from aiogram import BaseMiddleware
from aiogram.types import Message

from typing import Callable, Dict, Awaitable, Any
from cache3 import SafeCache
from loguru import logger

from app.models import User


class UserRegisterMiddleware(BaseMiddleware):
    #def __init__(self) -> None:
    #    self.counter = 0

    async def __call__(
                        self,
                        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                        event: Message,
                        data: Dict[str, Any]
                    ) -> Any:
        
        user_id: int = event.from_user.id
        username: str = event.from_user.username
        name: str = event.from_user.first_name
        
        
        user_model_cache = SafeCache('UserModels')
        
        if user_id in user_model_cache:
            user_model: User = SafeCache('UserModels')[user_id]
        else:
            user_model: User = await User.get_or_none(user_id=user_id)
            
            if not user_model:
                user_model: User = User(
                    user_id=user_id,
                    username=username,
                    name=name
                )
                
                await user_model.save()
            
            user_model_cache[user_id] = user_model

        data['user_model'] = user_model
        
        try:
            result = await handler(event, data)
            return result
        
        except SyntaxError as e:
            logger.error(str(e))