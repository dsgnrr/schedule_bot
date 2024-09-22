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
            teacher = Teacher.create(name=teacher_name)
            return result.Result(is_success=True,message=f"✅ Викладача <b>{teacher_name}</b> успішно додано",data=teacher)
        except Exception as e:
            return result.Result(False, message='🚫 При створені нового викладача виникла помилка')
        
    def edit_teacher(self, teacher_id:str, new_name:str=''):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "🚫 Невірний формат id")
        if new_name.strip() == '':
            return result.Result(False, "🚫 Ім'я не може бути пустим")
        uuid_obj = uuid.UUID(teacher_id, version=1) 
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            teacher.name = new_name
            teacher.save()
            return result.Result(True, f"✅ Ім'я викладача успішно змінено на: <b>{new_name}</b>")
        except DoesNotExist:
            return result.Result(False, "🙈 Викладачів не знайдено")
        
    def get_teacher_by_id(self, teacher_id):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "🚫 Невірний формат id") 
        uuid_obj = uuid.UUID(teacher_id, version=1) 
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            return result.Result(True, f"✅ Викладча знайдено", teacher)
        except DoesNotExist:
            return result.Result(False, "🙈 Викладачів не знайдено")
        
    def get_teachers(self):
        try:
            return Teacher.select()
        except Exception:
            return []
        
    def delete_teacher(self, teacher_id):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "🚫 Невірний формат id")
        uuid_obj = uuid.UUID(teacher_id, version=1)
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            teacher_name = teacher.name
            teacher.delete_instance()
            return result.Result(True, f"✅ Викладач <b>{teacher_name}</b> успішно видалений")
        except DoesNotExist:
            return result.Result(False, "🙈 Викладачів не знайдено")
        
class SubjectDao:
    def __init__(self) -> None:
        pass
    
    def create_new_subject(self, subject_name:str):
        if len(subject_name)> 150:
            return result.Result(False, '🚫 Максимальна кількість символів 150')
        subject = Subject().create(name=subject_name)
        return result.Result(is_success=True,message='✅ Предмет успішно створений', data=subject) 
    
    def change_teacher(self, subject_id:str, teacher_id:str):
        pass
    
    def get_subjects(self):
        try:
            return Subject.select()
        except Exception:
            return []