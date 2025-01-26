from schedule_parser.schemas.lesson import Lesson

class InvalidPDFError(Exception):
    def __init__(self):
        super().__init__('Не валидный PDF файл')


class PDFNotFoundError(Exception):
    def __init__(self, path: str):
        super().__init__(f'Файл расписания не найден: {path}')


class LessonValidationError(Exception):
    def __init__(self, error_type: str, lesson_data: Lesson):
        self.error_type = error_type
        self.lesson_data = lesson_data
        super().__init__(f'Type: \'{error_type}\', Lesson: {lesson_data}')
