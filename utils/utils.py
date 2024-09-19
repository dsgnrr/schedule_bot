import uuid

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
