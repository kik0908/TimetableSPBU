import unittest
import requests
from functools import reduce
from spbuTimetable import *


class TimetableTestsShort(unittest.TestCase):
    __headers = {'ru': {'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'},
                 'en': {}}

    def test_get_fields_of_study(self):
        data_ru = requests.get('https://timetable.spbu.ru/api/v1/study/divisions',
                               headers=TimetableTestsShort.__headers['ru']).json()
        # data_en = requests.get('https://timetable.spbu.ru/api/v1/study/divisions',
        #                        headers=TimetableTests.__headers['en']).json()
        with self.subTest('Ru get fields of study'):
            _ = get_fields_of_study('ru')
            self.assertEqual(len(data_ru), len(_.items()))
            for i in data_ru:
                self.assertEqual(i['Alias'], _[i['Name']])

        # with self.subTest('Eu get fields of study'):
        #     _ = get_fields_of_study('en')
        #     print(_)
        #     self.assertEqual(len(data_ru), len(_.items()))
        #     for i in data_en:
        #         self.assertEqual(i['Alias'], _[i['Name']])

    def test_get_programs(self):
        data_ru = requests.get('https://timetable.spbu.ru/api/v1/study/divisions/AMCP/programs/levels',
                               headers=TimetableTestsShort.__headers['ru']).json()

        with self.subTest(i='Ru test get_programs'):
            _ = get_programs('AMCP')
            _1 = reduce(lambda y, x: y + len(x['AdmissionYears']), data_ru[0]['StudyProgramCombinations'], 0)
            _2 = reduce(lambda y, x: y + len(x), _.values(), 0)
            self.assertEqual(_1, _2)

            for j in data_ru[0]['StudyProgramCombinations']:
                for k in j['AdmissionYears']:
                    self.assertEqual(k['StudyProgramId'], _[j['Name']][k['YearName']])

    def test_get_groups(self):
        _ = get_groups('AMCP', 11887)
        self.assertEqual(
            {'20.Б11-пу': ['AMCP', 303112], '20.Б12-пу': ['AMCP', 303111], '20.Б13-пу': ['AMCP', 303117],
             '20.Б15-пу': ['AMCP', 303074]}, _)


if __name__ == '__main__':
    unittest.main()
