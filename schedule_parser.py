import re
import datetime
import pdfplumber


class Parser():
    lesson_regex = re.compile(
        r'(.*?)\. (.*?) ?(лекции|семинар|лабораторные занятия)(.*?)\. ([^\.]*?)\.? \[(.*?)\]')
    dates_regex = re.compile(r'(\d{2})\.(\d{2})-(\d{2})\.(\d{2}) (ч.н.|к.н.)')
    single_date_regex = re.compile(r'(\d{2})\.(\d{2})')
    subgroup_regex = re.compile(r'\((А|Б)\)')

    def parse(self, path: str) -> list:
        table = pdfplumber.open(path).pages[0].extract_table()
        self.times = table[0]
        result = [elem for row in [self.items(
            elem, time) for row in table for time, elem in enumerate(row)] for elem in row]
        return result

    def items(self, object: str, time_index: str):
        lessons = []
        if object:
            while res := self.lesson_regex.search(object.replace('\n', ' ')):
                groups = res.groups()
                time = self.times[time_index]
                lesson = groups[0]
                professor = groups[1]
                type = groups[2]
                auditory = groups[4]
                dates = groups[5]
                subgroup = self.subgroup_regex.search(groups[3])
                if subgroup:
                    subgroup = subgroup[0]
                else:
                    subgroup = None
                if 'лабораторные занятия' in groups[2]:
                    time = self.times[time_index].split(
                        '-')[0] + '-' + self.times[time_index+1].split('-')[1]
                lessons.extend([(date, time, lesson, professor, type,
                               subgroup, auditory) for date in self.parse_date(dates)])
                object = object[res.end()+1:]
        return lessons

    @classmethod
    def parse_date(cls, date: str):
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
