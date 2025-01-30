import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pydantic_core import ValidationError

from schedule_parser import Parser
from schedule_parser.schemas.lesson import Lesson
from schedule_parser.exceptions.errors import PDFNotFoundError, InvalidPDFError
from schedule_parser.schemas.lesson import lesson_regex, professor_regex, auditory_regex

current_dir = os.path.dirname(__file__)
path_to_mock_pdf = os.path.join(current_dir, 'test.pdf')


def create_date(dat: str) -> datetime:
    day, month = map(int, dat.split('.'))
    year = datetime.today().year
    return datetime(year=year, month=month, day=day)


def test_lesson_regex():
    valid_lessons = [
        'Информационные технологии',
        'Управление техническими системами',
        'Физическая культура и спорт',
        'Русский язык (как иностранный)',
        'DevOps',
        'CAD-системы',
        'Сервисная робототехника: роботы в медицинских системах',
        'Оборудование цифровых производств. Интегрированные роботизированные системы',
        'Интегрированные CAE системы в машиностроении'
    ]

    for lesson in valid_lessons:
        assert lesson_regex.fullmatch(lesson)


def test_professor_regex():
    valid_professors = [
        'Юсеф Фарах',
        'Амир Абдаллах Д. А.',
        'Мягков А.С.',
        'Римский-Корсаков А.Л.',
        'Гайбу В.'
    ]

    invalid_professors = [
        'Юсеф Farax ',
        'Мягков А.С'
    ]

    for professor in valid_professors:
        assert professor_regex.fullmatch(professor)

    for professor in invalid_professors:
        assert not professor_regex.fullmatch(professor)


def test_auditory_regex():
    valid_auditories = [
        'Фрезер 303 (ММ)',
        'Фрезер 216 (ТП)',
        'Фрезер С/З',
        '235(в) - ТехП6',
        '216',
        '346/1',
        '346/4',
        '346/6',
        '501-7',
        '235(в) - ТехП6',
        'Фрезер 307',
        'Фрезер 203 (КК)',
        'РГГУ',
        '0803',
        'ТехП7',
        '442',
        'Актовый зал 1',
        'Стадион 2',
        'Фрезер 303 ОВП',
        'ИГ-1',
        'ТехП6(ГПА)',
        'Фрезер С/З 2'
    ]

    invalid_auditories = [
        'Фрезер - ',
        '304-',
        '-3',
        '345/',
        '/3',
        '135.4'
    ]

    for auditory in valid_auditories:
        assert auditory_regex.fullmatch(auditory)

    for auditory in invalid_auditories:
        assert not auditory_regex.fullmatch(auditory)


def test_lesson_validation_error():
    with pytest.raises(ValidationError) as e:
        Lesson(datetime_start=datetime(2025, 12, 21, 16, 10),
               datetime_end=datetime(2025, 12, 21, 15, 50),
               lesson='Иностранный язык\\',
               professor='Косова И.О',
               type='семинар',
               subgroup=None,
               auditory='Фрезер -',
               group='test')

    assert 'должна быть меньше даты окончания' in str(e.value)
    assert 'Неверный формат названия занятия' in str(e.value)
    assert 'Неверный формат имени преподавателя' in str(e.value)
    assert 'Неверный формат номера аудитории' in str(e.value)


def test_pdf_not_found_error():
    parser = Parser()
    non_existent_path = 'non_exist.pdf'
    with pytest.raises(PDFNotFoundError) as e:
        parser.parse(non_existent_path)

    assert str(e.value) == f'Файл расписания не найден: {non_existent_path}'


@patch('pdfplumber.open')
def test_invalid_pdf_error(mock_pdf_open):
    mock_pdf = Mock()
    mock_page = Mock()
    mock_page.extract_table.return_value = None
    mock_pdf.pages = [mock_page]
    mock_pdf_open.return_value = mock_pdf

    parser = Parser()
    with pytest.raises(InvalidPDFError) as e:
        parser.parse(path_to_mock_pdf)

    assert str(e.value) == 'Не валидный PDF файл'


def test_pdf_parsing():
    parser = Parser()
    result = parser.parse(path_to_mock_pdf)
    test_lessons = [
        'Иностранный язык', 'История России', 'Философия', 'Основы военной подготовки',
        'Математическая логика и теория алгоритмов', 'Объектно-ориентированное программирование', 'Физика',
        'Компьютерная графика и геометрия', 'Прикладная физическая культура', 'Аналитика данных и методы ИИ', 'Архитектура ЭВМ и вычислительных систем'
    ]
    test_professors = [
        'Косова И.О.', 'Лузгина Ю.С.', 'Шитов С.Б.', 'Красикова Е.М.', 'Елисеева Ю.В.',
        'Варварюк А.В.', 'Бельченко Ф.М.', 'Лоскутов А.И.', 'Терехов В.А.', 'Саркисова И.О.', 'Алешин В.И.'
    ]
    test_auditory = [
        '238', '0805', 'Фрезер 303 ОВП', '0408', 'Актовый зал 1', 'Стадион 2', '408', '235(з)'
    ]
    for lesson in test_lessons:
        assert lesson in [lesson.lesson for lesson in result]
    for professor in test_professors:
        assert professor in [lesson.professor for lesson in result]
    for auditory in test_auditory:
        assert auditory in [lesson.auditory for lesson in result]
    for lesson in result:
        assert lesson.professor != ''
        assert lesson.auditory != ''
        assert lesson.group is not None


def test_date_parsing():
    test_dates = ['01.09-15.09 ч.н.',
                  '01.09-02.09 ч.н.',
                  '11.08-11.08 к.н.']
    expected_results = [[create_date('01.09'), create_date('15.09')],
                        [create_date('01.09')],
                        [create_date('11.08')]]
    for test_date, expected in zip(test_dates, expected_results):
        assert Parser.parse_date(test_date) == expected


def test_lesson_parsing():
    test_lessons = ['Математика. Некто А.В. лекции. Фрезер 310. [11.03-18.03 к.н.,25.05]',
                    'Физика. лекции. СЗ Станкин. [21.03,22.03,25.05]',
                    'Базы данных. лекции. . [11.03-25.03 ч.н.,18.08]',
                    'Дифференциальные уравнения. Немо В.Д. семинар. . [15.05] ',
                    'Дифференциальные уравнения. Немо В.Д. лабораторные занятия (А). . [15.05]',
                    'Дифференциальные уравнения. Немо В.Д. лабораторные занятия (А). 311. [15.05]',
                    'Базы данных. Бычков С.Ю. семинар. . [11.01]',
                    'Базы данных. Бычков С.Ю. лабораторные занятия (А). . [11.01]',
                    'Базы данных. Бычков С.Ю. лабораторные занятия. . [11.01]',
                    'Базы данных. Бычков С.Ю. лабораторные занятия. Фрезер 303(ММ). [11.01]',
                    'Предмет. Предмет. Аль Хури А. лекции. 311. [11.03]',
                    'Предмет. Предмет. Предмет. Юсуф А. лекции. 311. [11.03]',
                    'Предмет. Предмет. Предмет. Юсуф А В Ф Ы А. лекции. 311. [11.03]']
    expected_results = [[(create_date('11.03'), 'Математика', 'Некто А.В.', 'лекции', None, 'Фрезер 310', ''),
                         (create_date('18.03'), 'Математика',
                          'Некто А.В.', 'лекции', None, 'Фрезер 310', ''),
                         (create_date('25.05'), 'Математика', 'Некто А.В.', 'лекции', None, 'Фрезер 310', '')],
                        [(create_date('21.03'), 'Физика', None, 'лекции', None, 'СЗ Станкин', ''),
                         (create_date('22.03'), 'Физика',
                          None, 'лекции', None, 'СЗ Станкин', ''),
                         (create_date('25.05'), 'Физика', None, 'лекции', None, 'СЗ Станкин', '')],
                        [(create_date('11.03'), 'Базы данных', None, 'лекции', None, None, ''),
                         (create_date('25.03'), 'Базы данных',
                          None, 'лекции', None, None, ''),
                         (create_date('18.08'), 'Базы данных', None, 'лекции', None, None, '')],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'семинар', None, None, '')],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'лабораторные занятия', 'А', None, '')],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'лабораторные занятия', 'А', '311', '')],
                        [(create_date('11.01'), 'Базы данных',
                          'Бычков С.Ю.', 'семинар', None, None, '')],
                        [(create_date('11.01'), 'Базы данных', 'Бычков С.Ю.',
                          'лабораторные занятия', 'А', None, '')],
                        [(create_date('11.01'), 'Базы данных', 'Бычков С.Ю.',
                          'лабораторные занятия', None, None, '')],
                        [(create_date('11.01'), 'Базы данных', 'Бычков С.Ю.', 'лабораторные занятия', None, 'Фрезер 303(ММ)', '')],
                        [(create_date('11.03'), 'Предмет. Предмет', 'Аль Хури А.', 'лекции', None, '311', '')],
                        [(create_date('11.03'), 'Предмет. Предмет. Предмет', 'Юсуф А.', 'лекции', None, '311', '')],
                        [(create_date('11.03'), 'Предмет. Предмет. Предмет', 'Юсуф А В Ф Ы А.', 'лекции', None, '311', '')]]
    for test_lesson, expected in zip(test_lessons, expected_results):
        assert Parser.items(test_lesson) == expected
