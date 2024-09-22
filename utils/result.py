class Result:
    def __init__(self, is_success:bool, message:str,data=None) -> None:
        self.is_success=is_success
        self.message=message
        self.data=data