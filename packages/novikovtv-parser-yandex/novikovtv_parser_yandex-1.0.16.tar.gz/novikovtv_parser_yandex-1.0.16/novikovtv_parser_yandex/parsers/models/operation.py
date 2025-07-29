from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OperationResponse(BaseModel):
    type: str = Field(..., alias='@type')
    rawData: str


class Operation(BaseModel):
    done: bool
    id: str
    description: str
    createdAt: datetime
    modifiedAt: datetime
    createdBy: str
    response: Optional[OperationResponse] = None

    queryText: Optional[str] = None
