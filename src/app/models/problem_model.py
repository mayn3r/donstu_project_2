from tortoise.models import Model
from tortoise import fields


class ProblemModel(Model):
    id = fields.IntField(pk=True) 
    
    problem = fields.CharField(200)
    answer = fields.CharField(50)
    
    filename = fields.CharField(20)
    path = fields.CharField(50)
    url = fields.CharField(80)
    level = fields.IntField(default=0)  # Уровень сложности пользователя
    
    regdate = fields.DatetimeField(auto_now_add=True)  # *Дата регистрации


    class Meta:
        table = 'problems'

    def __str__(self):
        return f'ProblemModel(id={self.id}, filename={self.filename})'