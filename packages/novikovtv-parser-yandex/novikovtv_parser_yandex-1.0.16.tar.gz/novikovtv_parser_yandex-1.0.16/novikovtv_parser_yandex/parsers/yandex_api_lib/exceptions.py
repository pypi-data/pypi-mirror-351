class HTTPError(Exception):
    """Ошибка получения http запроса (то есть not response.ok)"""
    pass


class HTTPBadPayloadError(Exception):
    """
    Класс ошибки при неверном теле (body) ответа
    """
    pass


class HTTPBadResponseError(Exception):
    """
    Класс ошибки при статусе ответа не равном 2xx
    """
    pass


class YandexRetryError(Exception):
    """
    Класс ошибки, означающий, что надо выполнить повторный запрос
    """

    def __init__(self, iteration: int):
        self.iteration = iteration
        super().__init__(f"Retry attempt {iteration}")
