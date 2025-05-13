from datetime import datetime
from typing import Tuple
from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID


class Report(BaseModel):
    '''Pydantic-модель для автоматической валидации данных из запроса и данных, извлеченных из чека'''

    date_and_time: datetime
    gps: Tuple[float, float]
    employee_id: UUID
    shop_id: UUID
    t: datetime
    s: Decimal
    fn: str = Field(min_length=16, max_length=16)
    i: int = Field(ge=0, le=9999999999)
    fp: int = Field(ge=0, le=9999999999)
    n: int
