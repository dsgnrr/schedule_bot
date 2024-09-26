import datetime
import uuid

from peewee import *
from .base_model import BaseModel
from .teacher import Teacher
from constants.hints import *

class Subject(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid1)
    name = CharField(max_length=150, null=False)
    teacher_id = ForeignKeyField(Teacher, to_field='id', backref='teacher', null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    deleted_at = DateTimeField(null=True)
    class Meta:
        table_name = 'subjects'
    def __str__(self) -> str:
        teacher_name = ''
        try:
            teacher_name = self.teacher_id.name
        except AttributeError:
            teacher_name = MISSING_TEACHER_HINT
        return f"📚 {self.name}\n👨‍🏫 {teacher_name}\n\n"