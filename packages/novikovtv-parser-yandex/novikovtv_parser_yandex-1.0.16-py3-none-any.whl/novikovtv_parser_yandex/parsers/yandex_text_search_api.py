from __future__ import annotations

import asyncio
import logging
import uuid
from asyncio import BoundedSemaphore
from datetime import datetime, timedelta, time as dt_time, timezone
from enum import Enum
from typing import Optional, Tuple

import aiohttp
from asynciolimiter import Limiter

from novikovtv_parser_yandex.parsers.models.operation import Operation
from novikovtv_parser_yandex.parsers.models.site_data import SiteParserData
from novikovtv_parser_yandex.parsers.search_links_parser import YandexSearchLinksParser
from novikovtv_parser_yandex.parsers.site_parser import SiteParser
from novikovtv_parser_yandex.parsers.yandex_api_lib.constants import PAGE_RANGE, RPS_V1, MAX_RETRY_ATTEMPTS
from novikovtv_parser_yandex.parsers.yandex_api_lib.exceptions import HTTPBadResponseError, YandexRetryError
from novikovtv_parser_yandex.parsers.yandex_api_lib.yandex_api import YandexAPI

# logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class ParserType(Enum):
    Day = 0
    Night = 1


async def wait_until(target_time: dt_time):
    """
    Ждет до указанного времени по UTC+3 (МСК).
    """
    tz = timezone(timedelta(hours=3))
    now_utc3 = datetime.now(tz=tz)
    now_utc3_time = now_utc3.time()

    target_datetime = datetime.combine(now_utc3.date(), target_time, tzinfo=tz)

    if now_utc3_time > target_time:
        target_datetime += timedelta(days=1)

    wait_seconds = (target_datetime - now_utc3).total_seconds()
    logger.debug(f"Ожидание {wait_seconds} секунд до {target_time} (UTC+3)")
    await asyncio.sleep(wait_seconds)


class YandexSearchTextApiV1(YandexAPI):
    """
    Класс для работы с Yandex Search API.
    Использует API_V1

    Этот класс предоставляет функциональность для создания запросов на поиск через API Яндекс и обработки
    отложенных поисковых операций. Поиск осуществляется в асинхронном режиме, а результаты сохраняются в
    файле для дальнейшего использования.

    Основные особенности:
    - Инициализация с чтением списка операций из файла, чтобы продолжить выполнение с сохранённых операций.
    - Асинхронная отправка поисковых запросов с использованием API Яндекс.
    - Отложенное выполнение запросов с сохранением и обновлением списка операций.
    - Возможность записи новых операций в файл для последующего использования.

    Атрибуты:
    - `operations_list`: Список объектов операций, представляющих отложенные поисковые запросы.
      Каждая операция сохраняется в файл после её создания.
    """

    @classmethod
    async def create(cls, *args, **kwargs) -> YandexSearchTextApiV1:
        """
        Асинхронная фабрика YandexSearchApiDeferred
        :param read: считывать ли по умолчанию operations из файла или нет
        :return:
        """
        baseInstance = await cls.__base__.create(*args, **kwargs)
        self_ = cls(*args, **kwargs)
        self_.__dict__.update(baseInstance.__dict__)

        return self_

    def __init__(self, api_key_v1: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations_list: list[Operation] = []
        self.semaphore = BoundedSemaphore(RPS_V1)
        self.limiter = Limiter(RPS_V1 / 1.0, max_burst=RPS_V1)

        self.__api_key_v1: str = api_key_v1

    def get_url_v1(self, query_text: str, *,
                   lr: int = 1,
                   l10n: str = "ru",
                   sort_by: str = "rlv",
                   page: int = 0,
                   filter: str = "moderate",
                   maxpassages: int = 4
                   ) -> str:
        """
        Возвращает URL для запроса к поисковому API
        """
        return (f"https://yandex.ru/search/xml/html?"
                f"folderid={self.FOLDER_ID}&"
                f"apikey={self.__api_key_v1}&"
                f"query={query_text}&"
                f"page={page}&"
                f"l10n={l10n}&"
                f"lr={lr}&"
                f"sortby={sort_by}&"
                f"filter={filter}&"
                f"maxpassages={maxpassages}&"
                f"groupby=attr%3Dd.mode%3Ddeep.groups-on-page%3D100.docs-in-group%3D1"
                )

    async def search(self, query_text: str, p_type: ParserType, search_id: int = None) -> Tuple[
        str, list[SiteParserData]]:
        """
        Отправляет поисковый запрос в Yandex API

        Args:
            search_id:
            query_text: Текст поискового запроса.
            p_type: тип парсера

        Returns
            search_id - Идентификатор поискового запроса
        """
        if search_id is None:
            search_id: str = str(uuid.uuid4())

        now_utc3_time: dt_time = datetime.now(tz=timezone(timedelta(hours=3))).time()
        if p_type.value == ParserType.Night.value:
            logger.debug("Ночной тип парсинга")
            await wait_until(dt_time(0, 0))
        elif p_type.value == ParserType.Day.value and dt_time(0, 0) <= now_utc3_time < dt_time(7, 0):
            logger.debug("Дневной тип парсинга")
            await wait_until(dt_time(7, 0))

        # tasks: list = [self.limiter.wrap((self.__try_search(query_text, page, folder_abs_path, search_id=search_id)))
        #                for page in PAGE_RANGE]
        tasks: list = [self.__try_search(query_text, page, search_id=search_id)
                       for page in PAGE_RANGE]

        site_parse_data_list: list[Optional[list[SiteParserData]]] = await asyncio.gather(*tasks)
        site_parse_data_list_filtered: list[SiteParserData] = [item for sublist in site_parse_data_list if
                                                               sublist is not None for item in sublist]

        return search_id, site_parse_data_list_filtered

    # TODO: решить проблему с одновременными запросами
    # Limiter и Semaphore не помогли, так как проблема именно в обращении к сайту, а в количестве активных потоков
    async def __fetch(self, query_text: str, page: int, *, search_id: int = 0,
                      iteration: int = 0) -> list[SiteParserData]:
        async with self.semaphore:
            await asyncio.sleep(1 / RPS_V1)
            async with aiohttp.ClientSession() as session:
                async with session.get(self.get_url_v1(query_text, page=page)) as response:
                    logger.debug(
                        f"Парсинг страницы {page} из {query_text}. Итерация {iteration}. Search-id: {search_id}"
                    )
                    if response.status != 200:
                        raise HTTPBadResponseError(
                            f"Request failed with status {response.status}. {await response.text()}"
                        )

                    text = await response.text()
                    if text.startswith("<?xml"):
                        if '<error code="55">' in text and iteration < MAX_RETRY_ATTEMPTS:
                            raise YandexRetryError(iteration + 1)

                        logger.warning(f"{response.status} {await response.text()}")
                        return None

                    htmlStr = text
                    yandex_search_parser = YandexSearchLinksParser(htmlStr)
                    links: list[str] = yandex_search_parser.parse()

                    site_parser = SiteParser(search_id)
                    site_parser_data_list: list[SiteParserData] = await site_parser.parse(links)
                    return site_parser_data_list

    async def __try_search(self, *args, iteration: int = 0, **kwargs) -> Optional[list[SiteParserData]]:
        try:
            return await self.__fetch(*args, **kwargs, iteration=iteration)
        except HTTPBadResponseError as e:
            logger.warning(f"HTTP ошибка: {e}")
        except YandexRetryError as yre:
            # logger.warning(f"Ошибка с повторной попыткой. Итерация = {yre.iteration}. Ожидание {1 / RPS_V1} сек.")
            await asyncio.sleep(1 / RPS_V1)
            await self.__try_search(*args, **kwargs, iteration=yre.iteration)
        except Exception as e_:
            logger.error(e_)

        return None


def make_csv_text(result: list[SiteParserData]) -> str:
    csv_text: str = SiteParserData.get_headers() + "\n"
    for result in result:
        csv_text += result.get_csv() + "\n"

    return csv_text


async def main():
    yandex_api = await YandexSearchTextApiV1.create(
        oauth_token="",
        folder_id="",
        api_key_v1="")
    a = await yandex_api.search("Novikov TV", ParserType.Day)


if __name__ == "__main__":
    asyncio.run(main())
