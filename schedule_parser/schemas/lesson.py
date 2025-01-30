from datetime import datetime
import re

from pydantic.dataclasses import dataclass
from pydantic import field_validator
from pydantic_core import PydanticCustomError
from schedule_parser.schemas.enums import SubgroupType, LessonType

lesson_regex: re.Pattern = re.compile(r'^[A-Za-zА-Яа-яЁё0-9 .,:"\+\/\(\)-]+$')
professor_regex: re.Pattern = re.compile(r'^[А-ЯЁ][А-Яа-яЁё-]+ (?: ?[А-ЯЁ]\.){1,2}|(?:[А-ЯЁ][А-Яа-яЁё-]+ ?){2,3}(?: ?[А-ЯЁ]\.){0,2}$')
auditory_regex: re.Pattern = re.compile(
    r'^(?:(?:[А-Яа-яЁё ]+)?(?:\d{1,4}(?:\/[\d])?(?:-[\d])?(?:\([а-я]\))?(?: *[-—] *[А-Яа-яЁё\d]+)?(?: *\([А-Яа-яЁё]+\))?(?: +[А-Яа-яЁё]+)?|С\/З(?: \d{1})?)|[А-Я]+|ИГ-\d+)$')


@dataclass
class Lesson():
    datetime_start: datetime
    datetime_end: datetime
    lesson: str
    professor: str | None
    type: LessonType
    subgroup: SubgroupType | None
    auditory: str | None
    group: str

    @field_validator('datetime_end')
    def validate_datetime(cls, datetime_end, info):
        datetime_start = info.data.get('datetime_start')
        if datetime_start and datetime_start >= datetime_end:
            raise PydanticCustomError(
                'invalid_datetime',
                f'Дата начала: {datetime_start} должна быть меньше даты окончания: {datetime_end}'
            )
        return datetime_end

    @field_validator('lesson')
    def validate_lesson(cls, lesson):
        if not lesson or len(lesson) > 150 or not lesson_regex.fullmatch(lesson):
            raise PydanticCustomError(
                'invalid_lesson_format',
                f'Неверный формат названия занятия: {lesson}'
            )
        return lesson

    @field_validator('professor')
    def validate_professor(cls, professor):
        if professor and (len(professor) > 50 or not professor_regex.fullmatch(professor)):
            raise PydanticCustomError(
                'invalid_professor_format',
                f'Неверный формат имени преподавателя: {professor}'
            )
        return professor

    @field_validator('auditory')
    def validate_auditory(cls, auditory):
        if auditory and not auditory_regex.fullmatch(auditory):
            raise PydanticCustomError(
                'invalid_auditory_format',
                f'Неверный формат номера аудитории: {auditory}'
            )
        return auditory
