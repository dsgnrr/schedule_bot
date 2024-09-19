import datetime
import uuid
from peewee import *
from .base_model import BaseModel
from .subject import Subject
from .teacher import Teacher

class Lesson(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid1)
    subject_id = ForeignKeyField(Subject, to_field='id', backref='subject', null=True)
    teacher_id = ForeignKeyField(Teacher, to_field='id', backref='teacher', null=True)
    start_time = CharField(max_length=6, null=True)
    end_time = CharField(max_length=6, null=True)
    lesson_date = DateTimeField(default=datetime.datetime.now, null=False)
    conference_link = TextField(null=True)
    class Meta:
        table_name = 'lessons'