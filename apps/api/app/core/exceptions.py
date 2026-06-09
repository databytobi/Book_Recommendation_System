class APIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400
    ):
        super().__init__(message)  # Pass message to parent Exception
        self.message = message
        self.status_code = status_code