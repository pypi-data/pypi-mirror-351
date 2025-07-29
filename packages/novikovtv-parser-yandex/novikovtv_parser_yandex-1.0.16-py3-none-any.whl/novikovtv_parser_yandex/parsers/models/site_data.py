from typing import Optional

from pydantic import BaseModel, Field


class SiteParserData(BaseModel):
    url: str
    title: str
    phones: Optional[str] = None
    emails: Optional[str] = None
    address: Optional[str] = None
    social_networks: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None

    @staticmethod
    def get_delimiter_for_fields() -> str:
        return "|"

    @staticmethod
    def get_csv_delimiter():
        return ";"

    @staticmethod
    def ignore_fields() -> list[str]:
        return []

    @classmethod
    def get_headers(cls) -> str:
        headers = []
        for column in cls.model_fields.keys():
            if column in SiteParserData.ignore_fields():
                continue

            headers.append(column)

        return cls.get_csv_delimiter().join(headers)

    def get_csv(self) -> str:
        values = []
        for column in self.model_fields.keys():
            if column in SiteParserData.ignore_fields():
                continue

            value = getattr(self, column)
            values.append(value if value is not None else "")
        return self.get_csv_delimiter().join(map(str, values))