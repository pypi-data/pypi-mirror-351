from novikovtv_parser_yandex.parsers.models.site_data import SiteParserData

# Парсер поисковой выдачи Яндекса

## Пример

```py


from enum import Enum

from pydantic import BaseModel

from novikovtv_parser_yandex.parsers.models.site_data import SiteParserData
from novikovtv_parser_yandex.parsers.yandex_text_search_api import YandexSearchTextApiV1, ParserType


class ParserRouteType(str, Enum):
    YANDEX: str = "yandex"
    FNS: str = "fns"
    VK: str = "vk"
    TENCHAT: str = "tenchat"


class ParserAPIType(int, Enum):
    """Перечисление типов парсера API."""
    Deferred = 0  # Отложенный парсинг
    Day = 1  # Дневной парсинг
    Night = 2  # Ночной парсинг


class ParserRequest(BaseModel):
    """Модель запроса на парсинг."""
    tg_user_id: int
    query: str
    type: ParserAPIType


async def yandex(parser_request: ParserRequest, search_id: int):
    """Выполняет парсинг Яндекса по запросу пользователя."""
    yandex_api = await YandexSearchTextApiV1.create(
        oauth_token="",
        folder_id="",
        api_key_v1="")

    p_type: ParserType = ParserType.Day
    if parser_request.type == ParserAPIType.Day.value:
        p_type = ParserType.Day
    elif parser_request.type == ParserAPIType.Night.value:
        p_type = ParserType.Night

    site_parse_data_list: list[SiteParserData]
    _, site_parse_data_list = await yandex_api.search(parser_request.query, p_type, search_id)
```