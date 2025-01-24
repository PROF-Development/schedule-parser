from datetime import datetime
from schedule_parser import Parser

path_to_mock_pdf = '/home/gkave/Downloads/test_wrong2.pdf'

parser = Parser()

lesson_data = {
    'datetime_start': datetime(2025, 12, 21, 14, 10),
    'datetime_end': datetime(2025, 12, 21, 15, 50),
    'lesson': 'Иностранный язык2',
    'professor': 'Косова И.О.',
    'type': 'семинар',
    'subgroup': None,
    'auditory': '238',
    'group': 'test'
}

try:
    p = parser.parse(path_to_mock_pdf)
    print(p)
except Exception as e:
    print(f"Got exception for group: group | {str(e)}", flush=True)
