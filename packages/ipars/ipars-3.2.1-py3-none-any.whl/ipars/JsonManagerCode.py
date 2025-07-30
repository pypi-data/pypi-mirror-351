import json
from pprint import pprint

class JsonManager:
    '''Класс для работы с json файлами во время парсинга'''

    def __init__(self, encoding: str = 'utf8'):
        '''Конструктор

        encoding: кодировка открываемого файла'''
        self.encoding = encoding

    def pprint(self, data: any) -> None:
        '''Выводим данные в удобочитаемом виде

        data: данные которые надо вывести'''
        pprint(data)

    def load(self, pathToJsonFile: str) -> json:
        '''Получаем данные из json файла

        pathToJsonFile: путь до json файла'''
        with open(pathToJsonFile, encoding=self.encoding) as jsonFile:
            src = json.load(jsonFile)
        return src

    def dump(self, pathToJsonFile: str, data: any) -> None:
        '''Записываем данные в json файл

        pathToJsonFile: путь до json файла
        data: данные которые надо записать'''
        with open(pathToJsonFile, 'w', encoding=self.encoding) as jsonFile:
            json.dump(data, jsonFile, indent=4, ensure_ascii=0)