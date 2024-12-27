from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)  # ID (уникальный иднтификатор) пользователя в БД
    user_id = fields.IntField()  # ID пользователя в телеграм
    username = fields.CharField(50, null=True)  # Короткое имя пользователя в телегарме
    name = fields.CharField(50)  # Имя пользователя в телеграме
    
    level = fields.IntField(default=0)  # Уровень сложности пользователя
    completed_tasks = fields.IntField(default=0)  # Кол-во решенных задач за 1 уровень
    completed_problems = fields.TextField(null=True)  # ID решенных задач

    
    regdate = fields.DatetimeField(auto_now_add=True)  # *Дата регистрации


    class Meta:
        table = 'users'

    def __str__(self):
        return f'User(id={self.id}, user_id={self.user_id})'