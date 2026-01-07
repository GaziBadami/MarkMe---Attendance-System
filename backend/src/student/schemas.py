from pydantic import BaseModel
from typing import Optional
from src.user.schemas import UserRoles

from utils.schemas.base import BaseSchema

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    enrollment_no: Optional[str] = None
    roll_no: Optional[str] = None
    course: Optional[str] = None
    div: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class StudentBase(BaseSchema, StudentUpdate):
    password: str

class StudentLoginRequest(BaseModel):
    enrollment_no: str
    password: str

class StudentResponse(StudentUpdate, BaseSchema):
    role: str = UserRoles.STUDENT.value
    is_active: bool = True
    is_banned: bool = False

    class Config:
        from_attributes = True

class StudentToken(BaseModel):
    user: StudentResponse
    token: str