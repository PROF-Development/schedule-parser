from datetime import datetime
import re

from pydantic.dataclasses import dataclass
from pydantic import field_validator
from pydantic_core import PydanticCustomError
from schedule_parser.schemas.enums import SubgroupType, LessonType

lesson_regex: re.Pattern = re.compile(r'^[А-Яа-яЁё\s,-]+$')
professor_regex: re.Pattern = re.compile(r'^[А-ЯЁ][а-яё-]+ [А-ЯЁ]\.(?:[А-ЯЁ]\.)?$')
auditory_regex: re.Pattern = re.compile(r'^(?:[А-Яа-яЁё\s]*\d+(?:\(\w+\))?(?:\s[А-Яа-яЁё\d]*)*|ИГ-\d+)$')  # Доработать регексу


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
        if not lesson or len(lesson) > 150 or not lesson_regex.match(lesson):
            raise PydanticCustomError(
                'invalid_lesson_format',
                f'Неверный формат названия занятия: {lesson}'
            )
        return lesson

    @field_validator('professor')
    def validate_professor(cls, professor):
        if professor and (len(professor) > 50 or not professor_regex.match(professor)):
            raise PydanticCustomError(
                'invalid_professor_format',
                f'Неверный формат имени преподавателя: {professor}'
            )
        return professor

    @field_validator('auditory')
    def validate_auditory(cls, auditory):
        if auditory and not auditory_regex.match(auditory):
            raise PydanticCustomError(
                'invalid_auditory_format',
                f'Неверный формат номера аудитории: {auditory}'
            )
        return auditory
