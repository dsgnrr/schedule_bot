import uuid
import os

from constants import *

def is_valid_uuid(param: str, version:int=1) -> bool:
    try:
        uuid_obj = uuid.UUID(param, version=version)
        return True
    except ValueError:
        return False
    
def truncate_string(input:str, after_symbol:str='_', part:int = 0):
    if len(input) == 0:
        return ''
    parts = input.split(after_symbol)
    if len(parts)>0:
        try:
            result = parts[part]
            return result
        except IndexError:
            return '' 
    return ''

# TODO: переписать эту фнукцию, она не универсальная
def read_text_file(env_path):
    try:
        base_dir = os.getcwd()
        text_file_path = os.getenv(env_path)
        if not text_file_path:
            return UNKNOWN_FUNCTION_ERROR
        file_path = os.path.join(os.path.join(base_dir, "wwwroot"), text_file_path)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден по пути {file_path}. {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при чтении файла: {e}")
    return UNKNOWN_FUNCTION_ERROR