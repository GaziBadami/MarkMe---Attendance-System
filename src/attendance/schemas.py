from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

from utils.schemas.base import BaseSchema
from src.attendance.enums import AttendanceEnum

class AttendanceUpdateSchema(BaseModel):
    student_id: Optional[str] = None
    qr_code_id: Optional[str] = None
    attendance_time: Optional[datetime] = None
    status: Optional[AttendanceEnum] = None
    created_at: Optional[datetime] = None
    day_label: Optional[str] = None
    qr_code_name: Optional[str] = None

    class Config:
        from_attributes  = True 

class AttendanceBaseSchema(BaseSchema, AttendanceUpdateSchema):
    pass
    class Config:
        from_attributes  = True 

class AttendanceRequestSchema(BaseModel):
    student_id: str
    qr_code_id: str
    status: Optional[AttendanceEnum] = None

class AttendanceResponseSchema(BaseModel):
    student_id: str
    student_first_name: str
    student_last_name: str
    student_roll_no: str
    student_enrollment: str
    student_roll_no: str
    attendance_time: datetime
    status: AttendanceEnum

    model_config = ConfigDict(from_attributes=True)