import datetime
import uuid
from peewee import *
from .base_model import BaseModel

class Teacher(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid1)
    name = CharField(max_length=150, null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    deleted_at = DateTimeField(null=True)
    class Meta:
        table_name = 'teachers'