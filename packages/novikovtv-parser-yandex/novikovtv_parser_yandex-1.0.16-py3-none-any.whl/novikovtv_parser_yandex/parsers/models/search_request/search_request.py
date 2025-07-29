from typing import Optional

from pydantic import BaseModel

from .search_additional_classes import *


class QuerySpec(BaseModel):
    """
    Модель для параметров запроса (например, текст поиска, фильтрация)
    """
    searchType: str = SearchType.SEARCH_TYPE_RU
    queryText: str = ""
    """Текст поискового запроса. Максимальная длина 400 символов."""

    page: str = "0"
    familyMode: str = FamilyMode.FAMILY_MODE_NONE
    fixTypoMode: str = FixTypoMode.FIX_TYPO_MODE_OFF


class SortSpec(BaseModel):
    """
    Модель для спецификации сортировки результатов поиска
    """
    sortMode: str = SortMode.SORT_MODE_BY_RELEVANCE
    sortOrder: str = SortOrder.SORT_ORDER_DESC


class GroupSpec(BaseModel):
    """
    Модель для спецификации группировки результатов поиска
    """
    groupMode: str = GroupMode.GROUP_MODE_DEEP
    groupsOnPage: int = 100
    """Максимальное количество групп на странице"""

    docsInGroup: int = 1
    """Максимальное количество документов в группе"""


class SearchRequestDeferred(BaseModel):
    """Модель для основного поискового запроса"""

    query: QuerySpec = QuerySpec()
    sortSpec: SortSpec = SortSpec()
    groupSpec: GroupSpec = GroupSpec()

    maxPassages: str = "4"
    """Максимальное количество пассажей, используемых при формировании сниппетов"""

    region: str = "Русский"
    """Идентификатор страны или региона, который влияет на правила ранжирования"""

    l10N: str = "LOCALIZATION_RU"
    """Язык уведомлений поискового ответа"""

    folderId: str
    """Идентификатор каталога пользователя или сервисного аккаунта"""

    responseFormat: str = "FORMAT_HTML"
    """Формат ответа (например, XML или HTML)"""

    userAgent: Optional[str] = None
    """Строка с заголовком User-Agent для устройства или браузера"""


if __name__ == "__main__":
    print(SearchRequestDeferred(folderId="").model_dump())
