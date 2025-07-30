import csv
from pprint import pprint

class CsvManager:
    '''Класс для работы с csv файлами во время парсинга'''

    def __init__(self, newline: str = '', encoding: str = 'utf8', delimiter: str = ';'):
        '''Конструктор

        newline: новая строка в csv файле
        encoding: кодировка открываемого файла
        delimiter: разделитель данных в csv файле'''
        self.newline = newline
        self.encoding = encoding
        self.delimiter = delimiter

    def pprint(self, data: any) -> None:
        '''Выводим данные в удобочитаемом виде

        data: данные которые надо вывести'''
        pprint(data)

    def writerow(self, filePath: str, mode: str, row: list) -> None:
        '''Записываем строку в csv файл

        filePath: путь до csv файла
        mode (w/a): метод открытия файла
        row: список записываемых данных'''
        with open(filePath, mode=mode, newline=self.newline, encoding=self.encoding) as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            writer.writerow(row)

    def writerows(self, filePath: str, mode: str, row: list) -> None:
        '''Записываем строки в csv файл

        filePath: путь до csv файла
        mode (w/a): метод открытия файла
        row: список записываемых данных'''
        with open(filePath, mode=mode, newline=self.newline, encoding=self.encoding) as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            writer.writerows(row)

    def getRows(self, filePath: str) -> list:
        '''Возвращает строки файла

        filePath: путь до csv файла'''
        userRows = []
        with open(filePath, mode='r', newline=self.newline, encoding=self.encoding) as csvfile:
            csvReader = csv.reader(csvfile, delimiter=self.delimiter)
            for row in csvReader:
                userRows.append(row)
        return userRows