import re
import datetime
import pdfplumber


class Parser:
    lesson_regex = re.compile(
        r'(.*?)\. (.*?) ?(лекции|семинар|лабораторные занятия)(.*?)\. ([^\.]*?)\.? \[(.*?)\]')
    dates_regex = re.compile(r'(\d{2})\.(\d{2})-(\d{2})\.(\d{2}) (ч.н.|к.н.)')
    single_date_regex = re.compile(r'(\d{2})\.(\d{2})')
    subgroup_regex = re.compile(r'\((А|Б)\)')
    times = ['8:30 - 10:10', '10:20 - 12:00', '12:20 - 14:00',
             '14:10 - 15:50', '16:00 - 17:40', '18:00 - 19:30',
             '19:40 - 21:10', '21:20 - 22:50']

    def parse(self) -> list:
        result = [elem for row in [self.items(
            elem, time) for row in self.table for time, elem in enumerate(row)] for elem in row]
        return result

    def read(self, path: str) -> bool:
        try:
            self.table = pdfplumber.open(path).pages[0].extract_table()
            return True
        except:
            return False

    @classmethod
    def items(cls, object: str, time_index: int = 0) -> list:
        lessons = []
        if object:
            while res := cls.lesson_regex.search(object.replace('\n', ' ')):
                groups = res.groups()
                time = cls.times[time_index-1]
                lesson = groups[0]
                professor = groups[1] if groups[1] != '' else None
                type = groups[2]
                auditory = groups[4] if groups[4] != '' else None
                dates = groups[5]
                subgroup = cls.subgroup_regex.search(groups[3])
                subgroup = subgroup[1] if subgroup else None
                if 'лабораторные занятия' in groups[2]:
                    time = cls.times[time_index-1].split(
                        '-')[0] + '-' + cls.times[time_index].split('-')[1]
                if time_index:
                    lessons.extend([(date, time, lesson, professor, type,
                                     subgroup, auditory) for date in cls.parse_date(dates)])
                else:
                    lessons.extend([(date, lesson, professor, type,
                                     subgroup, auditory) for date in cls.parse_date(dates)])
                object = object[res.end()+1:]
        return lessons

    @classmethod
    def parse_date(cls, date: str) -> list:
        dates = date.split(',')
        result_dates = []
        for el in dates:
            if 'к.н' in el or 'ч.н' in el:
                groups = cls.dates_regex.search(el).groups()
                start = datetime.date.today().replace(
                    month=int(groups[1]), day=int(groups[0]))
                end = datetime.date.today().replace(
                    month=int(groups[3]), day=int(groups[2]))
                period = 7 if 'к.н' in groups[4] else 14
                result_dates.extend([start + datetime.timedelta(days=i)
                                    for i in range(0, (end-start).days+1, period)])
            else:
                groups = cls.single_date_regex.search(el).groups()
                result_dates.append(datetime.date.today().replace(
                    month=int(groups[1]), day=int(groups[0])))
        return result_dates
