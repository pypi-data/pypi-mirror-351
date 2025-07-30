from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import pprint
from time import sleep
import requests

class Pars:
    '''Модуль для работы с запросами и bs4'''

    def returnBs4Object(self, pathToFile: str, encoding: str = 'utf8', parser: str = 'lxml'):
        '''Возвращаем объект beautifulsoup

        pathToFile: путь до html файла
        encoding: кодировка открытия html файла
        parser: парсер, который будет использоваться для работы'''
        with open(pathToFile, encoding=encoding) as file:
            src = file.read()
        soup = BeautifulSoup(src, parser)
        return soup

    def getTexts(self, arr: list, needFix: bool = 0) -> list:
        '''Возвращаем текст из элементов bs4
        
        arr: список объектов bs4 из которых будет извлекаться текст
        needFix (0/1): если этот параметр установлен как True, то из текста будут удалены \\n, \\t и пробелы с концов'''
        result = []
        for item in arr:
            data = item.text
            if needFix:
                data = data.strip()
                data = data.replace('\t', '')
                data = data.replace('\n', '')

            if not data:
                continue
            result.append(data)

        if not result:
            return None
        return result

    def getAttributes(self, arr: list, att: str) -> list:
        '''Возвращаем список значений атрибутов
        
        arr: список объектов bs4 из которых будет извлекаться атрибут
        att: строка с названием атрибута по которому будет осуществляться поиск'''
        result = []
        for item in arr:
            data = item.get(att)
            if data is not None:
                result.append(item.get(att))

        if not result:
            return None
        return result

    def pprint(self, data: any) -> None:
        '''Выводим данные в удобочитаемом виде

        data: данные которые надо вывести'''
        pprint(data)

    def getStaticPage(self, pathToSaveFile: str, url: str, writeMethod: str = 'w', headers: dict = None) -> int:
        '''Получаем статическую страницу и возвращаем статус ответа от сервера

        pathToSaveFile: путь, куда сохранится полученный файл
        url: ссылка на данные
        writeMethod: метод записи данных в файл. "W" записывает текст, "WB" — байты
        headers: заголовки запроса к серверу'''

        if headers is None:
            headers = {
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
            }

        try:
            # Отправляем запрос
            req = requests.get(url, headers=headers)

            # Записываем данные
            if writeMethod == 'w':
                src = req.text
                with open(pathToSaveFile, 'w', encoding='utf-8') as file:
                    file.write(src)

            elif writeMethod == 'wb':
                src = req.content
                with open(pathToSaveFile, 'wb') as file:
                    file.write(src)
            else:
                raise ValueError(f"Неподдерживаемый метод записи: {writeMethod}")

            return req.status_code  # Возвращаем статус ответа от сервера

        except requests.exceptions.HTTPError as httpErr:
            raise RuntimeError(f"HTTP ошибка: {httpErr}") from http_err
        except Exception as e:
            raise RuntimeError(e) from e

    def getDinamicPage(self, pathToSaveFile: str, url: str, closeWindow: bool = 1, timeSleep: int = 2) -> None:
        '''Получаем динамическую страницу

        pathToSaveFile: путь, куда сохранится полученный файл
        url: ссылка на данные
        closeWindow (0/1): если указана единица, то браузер открывается в фоновом режиме, 0 — открывается как обычное приложение
        timeSleep: время ожидания браузера перед тем как скролить страницу дальше'''

        # Устанавливаем опции для Chrome WebDriver
        options = Options()
        if closeWindow:
            options.add_argument('--headless')

        # открываем браузер
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            # Прокручиваем страницу до самого низа
            lastHeight = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Прокручиваем до низа страницы
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Ждем загрузки страницы
                sleep(timeSleep)
                # Вычисляем новую высоту страницы
                newHeight = driver.execute_script("return document.body.scrollHeight")
                if newHeight == lastHeight:
                    break
                lastHeight = newHeight

            # Получаем HTML-код страницы
            htmlContent = driver.page_source
            # Сохраняем HTML-код в файл
            with open(pathToSaveFile, "w", encoding="utf-8") as file:
                file.write(htmlContent)
