from datetime import datetime

from pydantic.dataclasses import dataclass

from schedule_parser.schemas.enums import SubgroupType, LessonType


@dataclass
class Lesson:
    datetime_start: datetime
    datetime_end: datetime
    lesson: str
    professor: str | None
    type: LessonType
    subgroup: SubgroupType | None
    auditory: str | None
    group: str
