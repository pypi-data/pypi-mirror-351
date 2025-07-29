import asyncio
import html
import logging
import re
from typing import Optional

import aiohttp
from aiohttp import ClientConnectorError
from bs4 import BeautifulSoup, Tag

from novikovtv_parser_yandex.parsers.models.site_data import SiteParserData


def get_address_string(all_addresses: list[tuple[str, str, str]]) -> list[str]:
    formatted_addresses = []
    for address in all_addresses:
        city, street, house = address
        formatted_address = f"г. {city}, ул. {street}, д. {house}"
        formatted_addresses.append(formatted_address)

    return formatted_addresses


def get_phone_numbers(all_phones: list[str]) -> list[str]:
    formatted_phones = []
    for phone in all_phones:
        phone_ = re.sub(r"\D", "", phone)
        formatted_phones.append(phone_)

    return formatted_phones


class SiteParser(object):
    """
    Класс для парсинга контактной информации (телефонов, email, социальных сетей, адресов) с веб-страниц.
    """

    def __init__(self, request_result_id: int):
        """
        Инициализирует регулярные выражения для поиска контактных данных.
        """
        self.request_result_id: int = request_result_id

        self._phone_pattern = re.compile(
            r"(?:tel:)?\b(?:\+7|7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b"
        )
        self._email_pattern = re.compile(
            r"[a-z0-9!#$%&'*+/=?^_{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
        )
        self._social_pattern = re.compile(
            r"https?:\/\/(?:"
            r"t\.me|"
            r"vk\.com|"
            r"wa\.com|"
            r"facebook\.com|"
            r"instagram\.com|"
            r"youtube\.com|"
            r"pinterest\.com|"
            r"linkedin\.com|"
            r"whatsapp\.com"
            r")\/[\w\d_]+"
        )
        self._address_pattern = re.compile(
            r"(?:г\.\s|город\s)?(Москва),?\s"  # Город Москва
            r"(?:ул\.\s|улица\s)([а-яА-Я\s-]+),?\s*"  # Улица
            r"(?:д\.\s)?(\d+[а-яА-Я]?(?:к\d+)?)"  # Дом
        )
        self.delimiter: str = SiteParserData.get_delimiter_for_fields()
        self.delimiter_for_csv: str = SiteParserData.get_csv_delimiter()

    async def parse(self, links: list[str]) -> list[SiteParserData]:
        """
        Обходит список ссылок и извлекает контактные данные с каждой страницы.

        :param links: Список URL-адресов для обработки.
        """
        tasks: list = [self.__try_parse_link(link) for link in links]
        site_parser_data_list: list[SiteParserData] = await asyncio.gather(*tasks)
        site_parser_data_list = [data for data in site_parser_data_list if data is not None]

        return site_parser_data_list

    async def __try_parse_link(self, link: str) -> Optional[SiteParserData]:
        try:
            return await self.__parse_link(link)
        except ClientConnectorError as e:
            logging.warning(f"Ошибка соединения с сайтом {link}")
        except Exception as e:
            logging.error(f"Link: {link}\nError: {e}")

    async def __parse_link(self, link: str) -> Optional[SiteParserData]:
        """
        Обходит список ссылок и извлекает контактные данные с каждой страницы.
        :param link: URL-адрес для обработки.
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                         timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(link) as response:
                if not response.ok:
                    logging.debug(f"Bad status {response.status}. Ссылка - {link}")
                    return None
                text = html.unescape(await response.text())
                text = text.replace('<br>', ' ')

                soup_ = BeautifulSoup(text, 'html.parser')

                description_tag: Optional[Tag] = soup_.find('meta', attrs={'name': 'description'})
                description: str = description_tag.get('content', ''). \
                    strip(). \
                    replace(self.delimiter_for_csv, ',') if description_tag else ''

                keywords_tag: Optional[Tag] = soup_.find('meta', attrs={'name': 'keywords'})
                keywords: str = keywords_tag.get('content', ''). \
                    strip(). \
                    replace(self.delimiter_for_csv, ',') if keywords_tag else ''

                title_tag: Optional[Tag] = soup_.find('title')
                title: str = title_tag.text. \
                    strip(). \
                    replace(self.delimiter_for_csv, ',') if title_tag and title_tag.text else ''

                # Удаляем лишние теги, чтобы по ним не происходил поиск регулярных выражений
                for tag in soup_.select('meta, style, link, script, iframe, img, video, br'):
                    tag.decompose()

                # Убираем аттрибуты у элементов (кроме тега <a>), чтобы по ним также не происходил поиск регулярных выражений
                for tag in soup_.find_all(True):
                    if tag.name not in ['a']:
                        tag.attrs = {}

                all_phones = get_phone_numbers(list(set(self._phone_pattern.findall(str(soup_)))))
                all_emails = list(set(self._email_pattern.findall(str(soup_))))
                all_socials = list(set(self._social_pattern.findall(str(soup_))))
                all_addresses = get_address_string(list(set(self._address_pattern.findall(str(soup_)))))

                if not any([all_phones, all_emails, all_socials, all_addresses]):
                    # Все данные отсутствуют
                    return None

                site_parser_data = SiteParserData(
                    url=link,
                    title=title,
                    phones=self.delimiter.join(all_phones),
                    emails=self.delimiter.join(all_emails),
                    address=self.delimiter.join(all_addresses),
                    social_networks=self.delimiter.join(all_socials),
                    description=description,
                    keywords=keywords,
                    request_result_id=self.request_result_id
                )
                return site_parser_data


if __name__ == '__main__':
    pass
