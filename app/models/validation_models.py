from datetime import datetime
from typing import Tuple
from pydantic import BaseModel
from fastapi import UploadFile
from uuid import UUID


class Report(BaseModel):
    gps_cords: Tuple[float, float]
    employee_id: UUID
    shop_id: UUID