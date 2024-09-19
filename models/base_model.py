from peewee import Model
from db.connection import db

class BaseModel(Model):
    class Meta:
        database = db