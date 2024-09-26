from models.homework import *  
from models.lesson import *  
from models.subject import *  
from models.teacher import * 
from utils import result
from utils import utils 
from .connection import db

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
        return Teacher.select()
        
    def delete_teacher(self, teacher_id):
        valid_res=utils.is_valid_uuid(teacher_id)
        if valid_res == False:
            return result.Result(False, "🚫 Невірний формат id")
        uuid_obj = uuid.UUID(teacher_id, version=1)
        try:
            teacher = Teacher.get(Teacher.id==uuid_obj)
            teacher_name = teacher.name
            SubjectDao().remove_teacher(teacher_id=teacher_id)
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
        return result.Result(is_success=True, message='✅ Предмет успішно створений', data=subject) 
    
    def change_subject_name(self, subject_id:str, subject_name:str):
        query = self.get_subject_by_id(subject_id=subject_id)
        if query.is_success == False:
            return query
        subject = query.data
        subject.name = subject_name
        subject.save()
        return result.Result(True, "✅ Назву предмета успішно змінено")
    
    def change_teacher(self, subject_id:str, teacher_id:str):
        teacher_result = TeacherDao().get_teacher_by_id(teacher_id=teacher_id)
        if teacher_result.is_success == False:
            return teacher_result
        subject_result = self.get_subject_by_id(subject_id=subject_id)
        if subject_result.is_success == False:
            return subject_result
        subject = subject_result.data
        subject.teacher_id = teacher_result.data.id
        with db.atomic():
            subject.save()
        return result.Result(True, "✅ Викладача предмету оновлено")
      
    def remove_teacher(self, teacher_id:str):
        teacher_result = TeacherDao().get_teacher_by_id(teacher_id=teacher_id)
        if teacher_result.is_success == False:
            return teacher_result
        teacher_name = teacher_result.data.name
        subjects = Subject.select().where(Subject.teacher_id==teacher_result.data.id)
        for subject in subjects:
            if subject !=None:
                subject.teacher_id = None
                subject.save()
        return result.Result(True, f"✅ Викладач <b>{teacher_name}</b> успішно видалений")
    
    def get_subject_by_id(self, subject_id:str):
        valid_res=utils.is_valid_uuid(subject_id)
        if valid_res == False:
            return result.Result(False, "🚫 Невірний формат id") 
        uuid_obj = uuid.UUID(subject_id, version=1) 
        try:
            subject = Subject.get(Subject.id==uuid_obj)
            return result.Result(True, f"✅ Предмет знайдено", subject)
        except DoesNotExist:
            return result.Result(False, "🙈 Предметів не знайдено")
         
    def get_subjects(self):
        return Subject.select()
    
    def delete_subject(self, subject_id):
        query = self.get_subject_by_id(subject_id=subject_id)
        if query.is_success == False:
            return query
        subject = query.data
        subject_name = subject.name
        subject.delete_instance()
        return result.Result(True, f"✅ Предмет <b>{subject_name}</b> успішно видалений")