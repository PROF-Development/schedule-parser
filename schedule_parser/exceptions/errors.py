class InvalidPDFError(Exception):
    def __init__(self):
        super().__init__('Не валидный PDF файл')


class PDFNotFoundError(Exception):
    def __init__(self, path: str):
        super().__init__(f'Файл расписания не найден: {path}')