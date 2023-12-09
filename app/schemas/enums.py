from enum import Enum


class LessonType(str, Enum):
    PRACTICE = 'семинар'
    LECTURE = 'лекции'
    LABORATORY = 'лабораторные занятия'


class SubgroupType(str, Enum):
    A = 'А'
    B = 'Б'
