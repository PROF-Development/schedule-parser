from datetime import date
from enum import Enum


class Lesson:
    def __init__(self, date: date, time: str, lesson: str, professor: str | None,
                 type: Enum, subgroup: Enum | None, auditory: str | None) -> None:
        self.date = date
        self.time = time
        self.lesson = lesson
        self.professor = professor
        self.type = type
        self.subgroup = subgroup
        self.auditory = auditory
