import datetime
import uuid
from peewee import *
from .base_model import BaseModel
from .subject import Subject

class Homework(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid1)
    subject_id = ForeignKeyField(Subject, to_field='id', backref='subject', null=True)
    added_date = DateTimeField(default=datetime.datetime.now, null=False)
    deadline_date = DateTimeField(default=datetime.datetime.now, null=False)
    task_text = TextField(null=False)
    materials_link = TextField(null=True)
    class Meta:
        table_name = 'homeworks'