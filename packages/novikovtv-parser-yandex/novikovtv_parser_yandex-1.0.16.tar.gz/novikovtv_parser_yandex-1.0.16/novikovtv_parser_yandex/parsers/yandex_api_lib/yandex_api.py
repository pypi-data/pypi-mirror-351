from __future__ import annotations

import asyncio
import dataclasses
import time

import aiohttp
from typing_extensions import deprecated

from novikovtv_parser_yandex.parsers.yandex_api_lib.constants import IAM_TIME_SECONDS_DELAY
from novikovtv_parser_yandex.util.singleton import singleton


@singleton
@dataclasses.dataclass
class IAM(object):
    token: str = ""
    timestamp: int = 0


class YandexAPI(object):
    """Базовый класс для работы с API Яндекса, использующий IAM токены для аутентификации.

    Этот класс обеспечивает получение и обновление IAM токена, который необходим для выполнения запросов к API Яндекса.
    Токен может быть получен с помощью OAuth 2.0 и используется для авторизации при обращении к API.
    Класс также обеспечивает управление временем жизни токена и его кэширование для предотвращения излишних запросов.

    Attributes:
        OAUTH_TOKEN (str): OAuth токен, используемый для получения IAM токена.
        FOLDER_ID (str): Идентификатор папки, используемый для работы с сервисами Яндекса.
        iam (IAM): Объект, содержащий IAM токен и время его получения.
        headers (dict): Заголовки, включая `Authorization`, для аутентификации запросов.
    """

    @classmethod
    async def create(cls, *args, **kwargs) -> YandexAPI:
        """Асинхронная фабрика для создания экземпляра YandexAPI.

        Returns:
            YandexAPI: Экземпляр YandexAPI с присвоенным (если не произошло ошибок) IAM токеном.
        """
        self_ = cls(*args, **kwargs)
        await self_.__refresh_IAM_token()
        return self_

    def __init__(self, oauth_token: str, folder_id: str, *args, **kwargs) -> None:
        """Инициализирует экземпляр YandexAPI.

        Устанавливает значения OAUTH_TOKEN и FOLDER_ID из переменных окружения.
        """
        self.OAUTH_TOKEN = oauth_token
        self.FOLDER_ID = folder_id
        self.iam: IAM = IAM()

    @property
    def headers(self) -> dict:
        """Возвращает заголовки для аутентификации запросов.

        Returns:
            dict: Заголовки, включая `Authorization` с IAM токеном.
        """
        return {
            "Authorization": f"Bearer {self.iam.token}"
        }

    async def __refresh_IAM_token(self) -> None:
        """Обновляет IAM токен, если это необходимо.

        Если токен существует и не истек, ничего не делает. В противном случае запрашивает новый токен
        и сохраняет его в базу данных.

        Raises:
            Exception: Если не удалось получить IAM токен.
        """
        # await self.__get_IAM_token_from_db()
        if self.iam is not None and (time.time() - self.iam.timestamp < IAM_TIME_SECONDS_DELAY):
            # Если IAM_TOKEN существует и не пришло время его обновлять, то ничего не делаем
            return

        async with (aiohttp.ClientSession() as session):
            async with session.post("https://iam.api.cloud.yandex.net/iam/v1/tokens",
                                    data='{"yandexPassportOauthToken": "' + self.OAUTH_TOKEN + '"}') as iamResponse:
                if not iamResponse.ok:
                    raise Exception("IAM token could not be getting")

                self.iam.token = (await iamResponse.json())['iamToken']
                self.iam.timestamp = time.time()

        # await self.__write_IAM_token_to_db()

    @deprecated("Больше не используется БД для IAM")
    async def __get_IAM_token_from_db(self) -> None:
        """Считывает IAM токен и время его получения из базы данных, если они там есть."""
        # self.iam = IAM()
        pass

    @deprecated("Больше не используется БД для IAM")
    async def __write_IAM_token_to_db(self) -> None:
        """Записывает IAM токен и время его получения в базу данных.

        Это позволяет сохранить токен для повторного использования при перезапуске программы.
        """
        #     IAM().token = self.iam.token
        #     IAM().timestamp = int(time.time())
        pass


async def main():
    yandex_api_lib = await YandexAPI.create()
    print(yandex_api_lib.iam)


if __name__ == "__main__":
    asyncio.run(main())
