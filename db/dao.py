from models.homework import *  
from models.lesson import *  
from models.subject import *  
from models.teacher import * 
from utils import result
from utils import utils 

class TeacherDao:
    def __init__(self) -> None:
        pass
    
    def create_new_teacher(self, teacher_name:str):
        try:
            Teacher.create(name=teacher_name)
            return result.Result(True,message='Викладача успішно додано')
        except Exception as e:
            return result.Result(False, message='При створені нового викладача виникла помилка')
        
    def edit_teacher(self, teacher_id:str, new_name:str=''):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "Невірний формат id")
        if new_name.strip() == '':
            return result.Result(False, "Ім'я не може бути пустим")
        uuid_obj = uuid.UUID(teacher_id, version=1) 
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            teacher.name = new_name
            teacher.save()
            return result.Result(True, f"Ім'я викладача успішно змінено на: {new_name}")
        except DoesNotExist:
            return result.Result(False, "Викладача не знайдено")
        
    def get_teachers(self):
        try:
            return Teacher.select()
        except Exception:
            return []
    def delete_teacher(self, teacher_id):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "Невірний формат id")
        uuid_obj = uuid.UUID(teacher_id, version=1)
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            teacher_name = teacher.name
            teacher.delete_instance()
            return result.Result(True, f"Викладач {teacher_name} успішно видалений")
        except DoesNotExist:
            return result.Result(False, "Викладача не знайдено") 