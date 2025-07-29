class SearchType(str):
    """Перечисление типов поиска"""

    SEARCH_TYPE_RU = "SEARCH_TYPE_RU"
    """Русский поиск"""

    SEARCH_TYPE_TR = "SEARCH_TYPE_TR"
    """Турецкий поиск"""

    SEARCH_TYPE_COM = "SEARCH_TYPE_COM"
    """Международный поиск"""


class FamilyMode(str):
    """Режим семейной фильтрации"""

    FAMILY_MODE_MODERATE = "FAMILY_MODE_MODERATE"
    """Умеренный фильтр (значение по умолчанию)"""

    FAMILY_MODE_NONE = "FAMILY_MODE_NONE"
    """Фильтрация отключена"""

    FAMILY_MODE_STRICT = "FAMILY_MODE_STRICT"
    """Семейный фильтр"""


class FixTypoMode(str):
    """Режим исправления опечаток"""

    FIX_TYPO_MODE_ON = "FIX_TYPO_MODE_ON"
    """Исправление опечаток включено (значение по умолчанию)"""

    FIX_TYPO_MODE_OFF = "FIX_TYPO_MODE_OFF"
    """Исправление опечаток отключено"""


class SortMode(str):
    """Режим сортировки результатов поиска"""

    SORT_MODE_BY_RELEVANCE = "SORT_MODE_BY_RELEVANCE"
    """По релевантности"""

    SORT_MODE_BY_TIME = "SORT_MODE_BY_TIME"
    """По времени изменения документа"""


class SortOrder(str):
    """Порядок сортировки"""

    SORT_ORDER_DESC = "SORT_ORDER_DESC"
    """Прямой порядок сортировки (значение по умолчанию)"""

    SORT_ORDER_ASC = "SORT_ORDER_ASC"
    """Обратный порядок сортировки"""


class GroupMode(str):
    """Режим группировки результатов"""

    GROUP_MODE_DEEP = "GROUP_MODE_DEEP"
    """Группировка по доменам (значение по умолчанию)"""

    GROUP_MODE_FLAT = "GROUP_MODE_FLAT"
    """Плоская группировка"""


class ResponseFormat(str):
    """Формат ответа"""

    FORMAT_XML = "FORMAT_XML"
    """Формат XML (значение по умолчанию)"""

    FORMAT_HTML = "FORMAT_HTML"
    """Формат HTML"""


class Localization(str):
    """Локализация ответа"""

    LOCALIZATION_RU = "LOCALIZATION_RU"
    """Русский (по умолчанию для русского поиска)"""

    LOCALIZATION_BE = "LOCALIZATION_BE"
    """Белорусский"""

    LOCALIZATION_KK = "LOCALIZATION_KK"
    """Казахский"""

    LOCALIZATION_UK = "LOCALIZATION_UK"
    """Украинский"""

    LOCALIZATION_TR = "LOCALIZATION_TR"
    """Турецкий"""

    LOCALIZATION_EN = "LOCALIZATION_EN"
    """Английский"""
