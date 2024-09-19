from .connection import db
from models.homework import *  
from models.lesson import *  
from models.subject import *  
from models.teacher import *  

def initialize_db():
    try:
        with db:
            db.create_tables([Teacher, Subject, Homework, Lesson], safe=True)
            print("Tables successfully created!")
    except OperationalError as e:
        print(f"DB connection error: {e}")
    except IntegrityError as e:
        print(f"Data error: {e}")
    except Exception as e:
        print(f"Unknown error: {e}")
       