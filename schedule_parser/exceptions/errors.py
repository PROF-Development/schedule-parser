class InvalidPDFError(Exception):
    def __init__(self, message="Не валидный PDF файл"):
        self.message = message
        super().__init__(self.message)


class PDFNotFoundError(Exception):
    def __init__(self, path: str):
        self.message = f"Файл расписания не найден: {path}"
        super().__init__(self.message)