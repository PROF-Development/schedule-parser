from enum import Enum


class LessonType(str, Enum):
    PRACTICE = 'Семинар'
    LECTURE = 'Лекция'
    LABORATORY = 'Лабораторная'


class SubgroupType(str, Enum):
    A = 'А'
    B = 'Б'
