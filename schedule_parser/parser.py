import datetime
import os
import re

import pdfplumber

from schedule_parser.schemas.lesson import Lesson


class Parser:
    lesson_regex = re.compile(
        r'(.*?)\. ?([А-Я][^.]+ [А-Я]\.(?:[А-Я]\.)?)? (лекции|семинар|лабораторные занятия)(?:.*?(А|Б).*?)??\. ([^\.]*?)??\.? \[(.*?)\]')
    dates_regex = re.compile(r'(\d{2})\.(\d{2})-(\d{2})\.(\d{2}) (ч.н.|к.н.)')
    single_date_regex = re.compile(r'(\d{2})\.(\d{2})')
    times = ['8:30 - 10:10', '10:20 - 12:00', '12:20 - 14:00',
             '14:10 - 15:50', '16:00 - 17:40', '18:00 - 19:30',
             '19:40 - 21:10', '21:20 - 22:50']

    def parse(self) -> list[Lesson]:
        result = [elem for row in [self.items(
            elem, time, self.group) for row in self.table for time, elem in enumerate(row)] for elem in row]
        return [Lesson(*lesson) for lesson in result]

    def read(self, path: str) -> None:
        self.group = os.path.basename(path).split('.pdf')[0]
        self.table = pdfplumber.open(path).pages[0].extract_table()
        if not self.table:
            raise TypeError('Не валидный PDF файл')

    @classmethod
    def items(cls, object: str, time_index: int = 0, group: str = '') -> list[tuple]:
        lessons = []
        if object:
            while res := cls.lesson_regex.search(object.replace('\n', ' ')):
                groups = res.groups()
                lesson = groups[0]
                professor = groups[1]
                type = groups[2]
                subgroup = groups[3]
                auditory = groups[4]
                dates = groups[5]
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
                groups = cls.dates_regex.search(el).groups()
                start = datetime.datetime(
                    year=year,
                    month=int(groups[1]),
                    day=int(groups[0]),
                )
                end = datetime.datetime(
                    year=year,
                    month=int(groups[3]),
                    day=int(groups[2])
                )
                period = 7 if 'к.н' in groups[4] else 14
                result_dates.extend([start + datetime.timedelta(days=i)
                                    for i in range(0, (end-start).days+1, period)])
            else:
                groups = cls.single_date_regex.search(el).groups()
                result_dates.append(datetime.datetime(
                    year=year,
                    month=int(groups[1]),
                    day=int(groups[0]),
                ))
        return result_dates