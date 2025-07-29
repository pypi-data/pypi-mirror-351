from __future__ import annotations

import asyncio
import base64
import logging
import os.path
import time
from typing import Coroutine, Any

import aiohttp
from aiohttp.web_exceptions import HTTPException
from pydantic import ValidationError

from db.models import Operation, OperationResponse
from db.repository.operations import OperationsRepository
from db.repository.repository import UnitOfWork
from novikovtv_parser_yandex.parsers.yandex_api_lib.exceptions import HTTPBadPayloadError, HTTPBadResponseError
from novikovtv_parser_yandex.parsers.yandex_api_lib.yandex_api import YandexAPI
from novikovtv_parser_yandex.parsers.yandex_api_lib.constants import REQUEST_DEFERRED_SEARCH_START_DELAY, REQUEST_DEFERRED_SEARCH, PAGE_RANGE
from novikovtv_parser_yandex.parsers.models.search_request.search_request import SearchRequestDeferred, QuerySpec


class _YandexSearchApiDeferredRequest(YandexAPI):
    """Класс для обработки отложенных поисковых запросов через Yandex Search API.

    TODO_: убрать '_' из названия класса, когда будет решено, что его надо использовать

    Этот класс используется для выполнения асинхронных запросов к API Яндекса,
    где запросы выполняются в отложенном режиме. Класс управляет процессом
    ожидания ответа, запрашивая статус операции до тех пор, пока не будет
    получен окончательный HTML-результат.

    Attributes:
        __operation (Operation): Объект `Operation`, содержащий информацию о поисковом запросе.
        __filename (str): Имя файла для сохранения HTML-результата.
        __abs_folder_path (str): Абсолютный путь к папке, куда сохраняется результат.

    Использование:
        ```python
        request = await YandexSearchApiDeferredRequest.create(operation)
        await request.start()
        ```
    """

    @classmethod
    async def create(cls, operation: Operation) -> _YandexSearchApiDeferredRequest:
        """Асинхронная фабрика для создания экземпляра YandexSearchApiDeferredRequest.

        Args:
            page (int): Страница поисковой выдачи
            operation (Operation): Объект `Operation`, содержащий информацию о запросе.

        Returns:
            _YandexSearchApiDeferredRequest: Экземпляр YandexSearchApiDeferredRequest с переданной операцией.
        """
        baseInstance = await cls.__base__.create()
        self_ = cls(operation)
        self_.__dict__.update(baseInstance.__dict__)
        return self_

    def __init__(self, operation: Operation):
        super().__init__()
        self.__operation = operation
        self.__page = self.__operation.page

        self.__folder_name = f"{self.__operation.queryText}".replace(" ", "_")
        self.__filename = f"{self.__folder_name}_{self.__page}.html"
        self.__abs_folder_path = os.path.abspath(f'../files/{self.__folder_name}')

        # if not os.path.exists(self.__abs_folder_path):
        #     os.mkdir(self.__abs_folder_path)

    async def start(self) -> str | None:
        """Запускает процесс получения HTML-ответа для отложенного поискового запроса.

        Сохраняет полученные страницы в папку с путем `self.__abs_folder_path`.

        Returns:
            str | None: Имя сохраненного HTML файла или None, если файл не получен.
        """
        if self.__operation is None:
            raise Exception("Объект operation не инициализирован!")

        htmlStr = await self.__send_until_getting_response()
        if htmlStr is None:
            logging.warning(f"HTML документ <{self.__operation.id}> не был получен")
            return

        # TODO: сделать запись в файл асинхронно
        # with open(f"{self.__abs_folder_path}/{self.__filename}", 'w', encoding='utf-8') as file:
        #     file.write(htmlStr)
        logging.debug(f"Save file in {self.__abs_folder_path}\\{self.__filename}")

        return os.path.abspath(self.__abs_folder_path)

    async def __send_until_getting_response(self) -> str | None:
        """Циклически отправляет запрос на получение результата операции, пока не получит ответ.

        Returns:
            str | None: HTML-ответ в виде строки или None, если ответ не получен.
        """
        timeDifference = time.time() - self.__operation.createdAt.timestamp()
        if timeDifference < REQUEST_DEFERRED_SEARCH_START_DELAY:
            logging.debug(
                f"Waiting {REQUEST_DEFERRED_SEARCH_START_DELAY - timeDifference} seconds before sending. Operation was created at {self.__operation.createdAt},"
                f" but we need to wait minimum {REQUEST_DEFERRED_SEARCH_START_DELAY} seconds before sending"
            )
            await asyncio.sleep(REQUEST_DEFERRED_SEARCH_START_DELAY - timeDifference)

        index = 1
        while True:
            try:
                logging.debug(f"Make {index}'s request for <{self.__operation.queryText}> page {self.__page}")

                htmlStr = await self.__try_getting_response()
                return htmlStr
            except HTTPBadResponseError as brr:
                logging.warning(brr)
                return None
            except HTTPBadPayloadError as bpr:
                await asyncio.sleep(REQUEST_DEFERRED_SEARCH)
                continue
            finally:
                index += 1

    async def __try_getting_response(self) -> str | None:
        """Пытается получить ответ от API для текущей операции.

        Выполняет запрос к API для получения статуса операции. Если ответ успешный и содержит данные,
        обрабатывает их и возвращает HTML-результат. В случае ошибок выбрасывает исключения.

        Args:
            index (int): Номер текущего запроса (используется для логирования).

        Returns:
            str | None: HTML-результат в виде строки, если ответ успешно обработан. В противном случае None.

        Raises:
            HTTPBadResponseError: Если ответ от API не успешный (например, код ответа не 200).
            HTTPBadPayloadError: Если ответ от API не содержит ожидаемого поля `response`.
            ValidationError: Если данные ответа не проходят валидацию через Pydantic.

        Notes:
            - В случае отсутствия поля `response` в ответе, метод выбрасывает исключение `HTTPBadPayloadError`.
            - Если ответ успешный, но данные не проходят валидацию, ошибка логируется, и метод возвращает None.
            - Поле `response.@type` переименовывается в `response.type` для корректной работы с Pydantic.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://operation.api.cloud.yandex.net/operations/{self.__operation.id}",
                                   headers=self.headers) as response:
                responseJson = await response.json()
                if not response.ok:
                    raise HTTPBadResponseError(
                        f"Ошибка при получении ответа. Статус {response.status}. Тело ответа: {responseJson}")

                if responseJson.get("response") is None:
                    raise HTTPBadPayloadError("Неверное тело запроса. Отсутствует поле response")

                # Переименование поля response.@type на response.type (то есть с @type на type)
                responseJson['response']['type'] = responseJson['response'].pop('@type')
                responseJson["response"] = OperationResponse(**responseJson["response"])
                try:
                    operationResponse = Operation(**responseJson)
                    operationResponse.format_date()
                    htmlStr = base64.b64decode(operationResponse.response.rawData).decode("utf-8")
                    await self.__complete_operation(operationResponse)
                    return htmlStr
                except ValidationError as e:
                    logging.warning(e)
                    return None

    async def __complete_operation(self, new_operation: Operation):
        """Завершает операцию, обновляя её статус и сохраняя результат в базе данных.

        Args:
            new_operation (Operation): Объект операции, которую необходимо завершить.
        """
        async with UnitOfWork() as uow:
            repository = OperationsRepository(uow)
            await repository.update(
                await repository.get(self.__operation.id),
                new_operation,
                raw_data=self.__abs_folder_path
            )


class _YandexSearchApiDeferred(YandexAPI):
    """Класс для работы с Yandex Search API с отложенным выполнением запросов.
    Использует API_V2.

    TODO_: убрать '_' из названия класса, когда будет решено, что его надо использовать

    Этот класс предоставляет функциональность для создания запросов на поиск через API Яндекс и обработки
    отложенных поисковых операций. Поиск осуществляется в асинхронном режиме, а результаты сохраняются в
    файле для дальнейшего использования.

    Attributes:
        operations_list (list[Operation]): Список объектов операций, представляющих отложенные поисковые запросы.
    """

    @classmethod
    async def create(cls, *, read=False) -> _YandexSearchApiDeferred:
        """Асинхронная фабрика для создания экземпляра YandexSearchApiDeferred.

        Args:
            read (bool, optional): Считывать ли операции из базы данных по умолчанию. По умолчанию False.

        Returns:
            _YandexSearchApiDeferred: Экземпляр YandexSearchApiDeferred.
        """
        baseInstance = await cls.__base__.create()
        self_ = cls()
        self_.__dict__.update(baseInstance.__dict__)
        if read:
            await self_.refresh_operations_from_db()

        return self_

    def __init__(self):
        super().__init__()
        self.operations_list: list[Operation] = []

    async def refresh_operations_from_db(self) -> None:
        """Читает список операций из базы данных и загружает их в память.

        Returns:
            None
        """
        filenamesList: list[str] = []
        tasks: list[Coroutine[Any, Any, str]] = []
        async with UnitOfWork() as uow:
            repository = OperationsRepository(uow)
            for operation in await repository.get_all():
                if operation.done:
                    filenamesList.append(operation.response.rawData)
                    continue

                tasks.append(self.__append_operation(operation, write=False))

        filenamesList.extend(await asyncio.gather(*tasks))
        return filenamesList

    async def search(self, query_text: str) -> str:
        """Отправляет поисковый запрос в Yandex API и добавляет операцию в список.

        Args:
            query_text (str): Текст поискового запроса.

        Returns:
            str: Имя полученного HTML файла.
        """
        filepath: str = ""
        tasks: list[Coroutine[Any, Any, str]] = []
        for page in PAGE_RANGE:
            searchRequestBody = SearchRequestDeferred(
                query=QuerySpec(
                    queryText=query_text,
                    page=str(page),
                ),
                folderId=self.FOLDER_ID
            )
            operation: Operation = await self.__get_operation_object(searchRequestBody)
            operation.page = page
            operation.queryText = query_text  # Если не поставить `query_text`, то `operation.queryText` будет равен None
            tasks.append(self.__append_operation(operation, write=True))

        return await asyncio.gather(*tasks)

    async def __append_operation(self, operation: Operation, *, write: bool = False) -> str:
        """Добавляет новую операцию в список и записывает её в базу данных при необходимости.

        Args:
            operation (Operation): Объект операции.
            write (bool, optional): Флаг, указывающий, нужно ли записывать операцию в базу данных. По умолчанию False.

        Returns:
            str: Имя полученного HTML файла.
        """
        self.operations_list.append(operation)
        if write:
            await self.__add_operation_to_db(operation)

        yandexSearchApiDeferredRequest = await _YandexSearchApiDeferredRequest.create(operation)
        return await yandexSearchApiDeferredRequest.start()

    async def __add_operation_to_db(self, operation: Operation) -> None:
        """Записывает операцию в базу данных.

        Args:
            operation (Operation): Объект операции.
        """
        async with UnitOfWork() as uow:
            repository = OperationsRepository(uow)
            operation.format_date()
            await repository.add(operation)

    async def __get_operation_object(self, body: SearchRequestDeferred) -> Operation:
        """Отправляет запрос на создание отложенного поиска в Yandex API.

        Args:
            body (SearchRequestDeferred): Объект с параметрами поиска.

        Returns:
            Operation: Объект операции, представляющий отложенный запрос.

        Raises:
            HTTPException: Если произошла ошибка при получении объекта операции.
            Exception: Если не удалось получить объект операции.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post("https://searchapi.api.cloud.yandex.net/v2/web/searchAsync",
                                    json=body.model_dump(),
                                    headers=self.headers) as operationResponse:
                if not operationResponse.ok:
                    raise HTTPException(text="Ошибка получения Operation объекта")

                operation = Operation(**await operationResponse.json())
                return operation

        raise Exception("Не удалось получить Operation объект")


async def main():
    yandex_api = await _YandexSearchApiDeferred.create()
    # fileList = await yandex_api.search("Премиальный салоны красоты Москва")
    fileList = await yandex_api.refresh_operations_from_db()
    print(fileList)


if __name__ == "__main__":
    asyncio.run(main())
