from datetime import date
import re

from pydantic import field_validator
from pydantic.dataclasses import dataclass

from app.schemas.enums import SubgroupType, LessonType


@dataclass
class Lesson:
    date: date
    time: str
    lesson: str
    professor: str | None
    type: LessonType
    subgroup: SubgroupType | None
    auditory: str | None

    @field_validator('time')
    def validate_time(cls, v):
        if not re.match(r'\d{1,2}:\d{2} - \d{2}:\d{2}',v):
            raise ValueError('Time must like 12:34 - 12:34')
        return v
