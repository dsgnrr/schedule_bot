from .utils import truncate_string
 
class Command:
    def __init__(self, full_command:str=None) -> None:
        self.crud_command = self.entity = self.target_entity_id = self.field_name = self.selected_id = ''
        if full_command != None:
            self.crud_command = truncate_string(full_command)
            self.entity= truncate_string(full_command, part = 1)
            self.target_entity_id = truncate_string(full_command, part = 2)
            self.field_name = truncate_string(full_command, part = 3)
            self.selected_id = truncate_string(full_command, part=4)
    def __str__(self) -> str:
        if len(self.field_name) != 0:
            if len(self.selected_id) != 0:
                return f"{self.crud_command}_{self.entity}_{self.target_entity_id}_{self.field_name}_{self.selected_id}"
            return f"{self.crud_command}_{self.entity}_{self.target_entity_id}_{self.field_name}"
        return f"{self.crud_command}_{self.entity}_{self.target_entity_id}"