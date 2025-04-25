from datetime import datetime
from typing import Tuple
from decimal import Decimal
from pydantic import BaseModel
from uuid import UUID


class Report(BaseModel):
    date_and_time: datetime
    gps: Tuple[float, float]
    employee_id: UUID
    shop_id: UUID
    t: datetime
    s: Decimal
    fn: int
    i: int
    fp: int
    n: int
