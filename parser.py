import pdfplumber
import re

file = 'test.pdf'
tables = pdfplumber.open(file)
page = tables.pages[0].extract_table()
class Parser(object):
    def __init__(self):
        self.lesson_regex = r'(.*?)\. (.*?) ?(лекции|семинар|лабораторные занятия.*?)\. ([^\.]*?)\.? \[(.*?)\]'

    def parse(self, pdf_file : str) -> list:
        table = pdfplumber.open(pdf_file).pages[0].extract_table()
        self.times = table[0]
        result = [elem for row in [self.items(elem, self.times[time]) for row in page for time,elem in enumerate(row)] for elem in row]
        return result
    def items(self, object : str, time : str):
        lessons = []
        if object:
            while True:
                res = re.search(self.lesson_regex, object.replace('\n', ' '))
                if res:
                    lessons.append((time,)+res.groups())
                else:
                    break
                object = object[res.end()+1:]

        return lessons

import csv
a = Parser().parse(file)
with open('my_data.csv', 'w', newline='') as csvfile:
    csv_writter = csv.writer(csvfile)
    csv_writter.writerows(a)