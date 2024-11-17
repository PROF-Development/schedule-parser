import datetime
import os
import re

import pdfplumber

from schedule_parser.schemas.lesson import Lesson
from schedule_parser.exceptions.errors import InvalidPDFError, PDFNotFoundError


class Parser:
    lesson_regex = re.compile(
        r'(.*?)\. ?([А-Я][^.]+ [А-Я]\.(?:[А-Я]\.)?)? (лекции|семинар|лабораторные занятия)(?:.*?(А|Б).*?)??\. ([^\.]*?)??\.? \[(.*?)\]')
    dates_regex = re.compile(r'(\d{2})\.(\d{2})-(\d{2})\.(\d{2}) (ч.н.|к.н.)')
    single_date_regex = re.compile(r'(\d{2})\.(\d{2})')
    times = ['8:30 - 10:10', '10:20 - 12:00', '12:20 - 14:00',
             '14:10 - 15:50', '16:00 - 17:40', '18:00 - 19:30',
             '19:40 - 21:10', '21:20 - 22:50']

    def parse(self, path: str) -> list[Lesson]:
        if not os.path.exists(path):
            raise PDFNotFoundError(path)
        
        self.group = os.path.basename(path).split('.pdf')[0]
        self.table = pdfplumber.open(path).pages[0].extract_table()
        if not self.table:
            raise InvalidPDFError()
        
        result = []
        for row in self.table[1:]:
            for time_index, cell_content in enumerate(row[1:], 1):
                if not cell_content:
                    continue
                    
                lessons = self.items(cell_content, time_index, self.group)
                result.extend(lessons)
        
        return [Lesson(*lesson_data) for lesson_data in result]

    @classmethod
    def items(cls, object: str, time_index: int = 0, group: str = '') -> list[tuple]:
        lessons = []
        if object:
            while res := cls.lesson_regex.search(object.replace('\n', ' ')):
                lesson, professor, type, subgroup, auditory, dates = res.groups()
                if type == 'лабораторные занятия':
                    time = cls.times[time_index-1].split(
                        '-')[0] + '-' + cls.times[time_index].split('-')[1]
                else:
                    time = cls.times[time_index-1]
                if time_index:
                    hour_start, minute_start, hour_end, minute_end = [
                        int(value) for part in time.split('-') for value in part.split(':')]
                    lessons.extend([(date.replace(hour=hour_start, minute=minute_start),
                                     date.replace(hour=hour_end, minute=minute_end),
                                     lesson,
                                     professor,
                                     type,
                                     subgroup,
                                     auditory,
                                     group,
                                     ) for date in cls.parse_date(dates)])
                else:
                    lessons.extend([(date,
                                     lesson,
                                     professor,
                                     type,
                                     subgroup,
                                     auditory,
                                     group,
                                     ) for date in cls.parse_date(dates)])
                object = object[res.end()+1:]
        return lessons

    @classmethod
    def parse_date(cls, date: str) -> list[datetime.date]:
        year = datetime.date.today().year
        dates = date.split(',')
        result_dates = []
        for el in dates:
            if 'к.н' in el or 'ч.н' in el:
                start_day, start_month, end_day, end_month, period = cls.dates_regex.search(el).groups()
                start = datetime.datetime(
                    year=year,
                    month=int(start_month),
                    day=int(start_day),
                )
                end = datetime.datetime(
                    year=year,
                    month=int(end_month),
                    day=int(end_day)
                )
                step = 7 if 'к.н' in period else 14
                result_dates.extend([start + datetime.timedelta(days=i)
                                    for i in range(0, (end-start).days+1, step)])
            else:     
                day, month = cls.single_date_regex.search(el).groups()
                result_dates.append(datetime.datetime(
                    year=year,
                    month=int(month),
                    day=int(day),
                ))
        return result_dates
