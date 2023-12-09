from datetime import date

from app.schedule_parser import Parser
from app.schemas.lesson import Lesson


def test_pdf_reading():
    parser = Parser()
    path_to_mock_pdf = 'test.pdf'
    assert parser.read(path_to_mock_pdf)


def test_pdf_parsing():
    parser = Parser()
    path_to_mock_pdf = 'test.pdf'
    parser.read(path_to_mock_pdf)
    result = [Lesson(*lesson) for lesson in parser.parse()]
    print(parser.parse())
    test_lessons = ['Проектирование информационных систем',
                    'Методы и алгоритмы теории игр',
                    'DevOps',
                    'Базы данных',
                    'Основы Web- технологий',
                    'Прикладная физическая культура',
                    'Теория конечных автоматов',
                    'Теория вероятностей, математическая статистика и случайные процессы',
                    'Машинное обучение и интеллектуальные системы',
                    'Моделирование и анализ бизнес-процессов']
    test_professors = ['Елисеева Н.В.',
                       'Елисеева Ю.В.',
                       'Сосенушкин С.Е.',
                       'Бычков С.Ю.',
                       'Подвигина Е.А.',
                       'Бекмурзаев В.А.',
                       'Владимиров А.Л.',
                       'Незнанов Ю.А.',
                       'Бычкова Н.А.',
                       'Коробов Н.А.',
                       None]
    test_auditory = ['311', '0811', '308', '209', '450', '0806', 'С/З СТАНКИН 1',
                     '0402', '0411', '0303', '214', '357(з)', '235(и)', '235(з)',
                     '306(а)', '235(д)', 'Фрезер 303 (ММ)']
    for lesson in test_lessons:
        assert lesson in [lesson.lesson for lesson in result]
    for professor in test_professors:
        assert professor in [lesson.professor for lesson in result]
    for auditory in test_auditory:
        assert auditory in [lesson.auditory for lesson in result]
    for lesson in result:
        assert lesson.professor != ''
        assert lesson.auditory != ''


def create_date(dat: str) -> date:
    day, month = map(int, dat.split('.'))
    return date.today().replace(month=month, day=day)


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
                    'Базы данных. Бычков. семинар. . [11.01]',
                    'Базы данных. Бычков. лабораторные занятия (А). . [11.01]',
                    'Базы данных. Бычков. лабораторные занятия. . [11.01]',
                    'Базы данных. Бычков. лабораторные занятия. Фрезер 303(ММ). [11.01]']
    expected_results = [[(create_date('11.03'), 'Математика', 'Некто А.В.', 'лекции', None, 'Фрезер 310'),
                         (create_date('18.03'), 'Математика',
                          'Некто А.В.', 'лекции', None, 'Фрезер 310'),
                         (create_date('25.05'), 'Математика', 'Некто А.В.', 'лекции', None, 'Фрезер 310')],
                        [(create_date('21.03'), 'Физика', None, 'лекции', None, 'СЗ Станкин'),
                         (create_date('22.03'), 'Физика',
                          None, 'лекции', None, 'СЗ Станкин'),
                         (create_date('25.05'), 'Физика', None, 'лекции', None, 'СЗ Станкин')],
                        [(create_date('11.03'), 'Базы данных', None, 'лекции', None, None),
                         (create_date('25.03'), 'Базы данных',
                          None, 'лекции', None, None),
                         (create_date('18.08'), 'Базы данных', None, 'лекции', None, None)],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'семинар', None, None)],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'лабораторные занятия', 'А', None)],
                        [(create_date('15.05'), 'Дифференциальные уравнения',
                          'Немо В.Д.', 'лабораторные занятия', 'А', '311')],
                        [(create_date('11.01'), 'Базы данных',
                          'Бычков.', 'семинар', None, None)],
                        [(create_date('11.01'), 'Базы данных', 'Бычков.',
                          'лабораторные занятия', 'А', None)],
                        [(create_date('11.01'), 'Базы данных', 'Бычков.',
                          'лабораторные занятия', None, None)],
                        [(create_date('11.01'), 'Базы данных', 'Бычков.', 'лабораторные занятия', None, 'Фрезер 303(ММ)')]]
    for test_lesson, expected in zip(test_lessons, expected_results):
        assert Parser.items(test_lesson) == expected
