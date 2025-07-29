import re

from bs4 import BeautifulSoup


class YandexSearchLinksParser(object):
    """
    Класс для парсинга ссылок из HTML-файла с результатами поиска Яндекса.

    Данный парсер извлекает ссылки из поисковой выдачи, игнорируя домены, указанные в списке IGNORE_LINKS.
    """
    IGNORE_LINKS = [
        'yandex.ru',
        'youtube.com',
        'www.youtube.com',
        '2gis.ru',
        'zoon.ru',
        'vk.com',
        'dzen.ru',
        'tenchat.ru',
        't.me',
        'dtf.ru',
        'hh.ru',
        'yabs.yandex.ru',
        'spravka-region.ru',
        'fooby.ru',
        'tindal.ru'
    ]

    @classmethod
    def is_ignored(cls, domain: str) -> bool:
        """Проверяет, содержится ли домен в списке игнорируемых."""
        return domain in cls.IGNORE_LINKS

    def __init__(self, html_str: str):
        """
        Инициализация парсера.

        :param html_str: Путь к HTML-файлу, содержащему результаты поиска Яндекса.
        """
        self._domain_pattern = re.compile(r"https?://([^/]+)")
        self._soup = BeautifulSoup(html_str, 'html.parser')

    def parse(self) -> list[str]:
        """
        Извлекает ссылки из поисковой выдачи, исключая нежелательные домены.

        :return: Список URL-адресов, полученных из результатов поиска.
        """
        links = []
        for link in self._links:
            domain_match = self._domain_pattern.match(link)
            if not domain_match or self.__class__.is_ignored(domain_match.group(1)):
                continue

            links.append(link)

        return links

    @property
    def _links(self) -> list[str]:
        """
        Собирает все ссылки из HTML-документа.

        :return: Список всех URL-адресов, найденных в документе.
        """
        return [li.attrs['href'] for li in self._soup.select('ul#search-result li.serp-item a.OrganicTitle-Link')]
