from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict

from src.attendance.schemas import AttendanceResponseSchema
from utils.schemas.base import BaseSchema

class QrCodeUpdateSchema(BaseModel):
    name: Optional[str] = None
    qr_code_data: Optional[Dict] = None
    expiry_time: Optional[datetime] = None
    regenerate_interval_seconds: Optional[float] = None

class QrCodeBaseSchema(BaseSchema, QrCodeUpdateSchema):
    updated_by: str

    model_config = ConfigDict(from_attributes=True)

class QrCodeRequestSchema(BaseModel):
    name: str
    expiry_time: datetime
    regenerate_interval_seconds: float

class QrCodeResponseSchema(QrCodeBaseSchema):
    attendance: Optional[List[AttendanceResponseSchema]] = None
    present_percentage: Optional[float] = None
    total_students: Optional[int] = None
    present_students: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)