from enum import Enum


class LessonType(str, Enum):
    SEM = 'семинар'
    LECTURE = 'лекции'
    LAB = 'лабораторные занятия'


class SubgroupType(str, Enum):
    A = 'А'
    B = 'Б'
