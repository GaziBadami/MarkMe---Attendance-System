from typing import Optional
from sqlalchemy.orm import Session

from src.attendance.models import Attendance
from src.attendance.schemas import AttendanceBaseSchema, AttendanceUpdateSchema

from utils.crud.base import CRUDBase

class AttendanceCRUD(CRUDBase[Attendance, AttendanceBaseSchema, AttendanceUpdateSchema]):
    def get_all_attendance_count(self, db: Session):
        return db.query(Attendance).count()

    def get_by_user_and_qr_id(self, db: Session, student_id: str, qr_code_id: str) -> Optional[Attendance]:
        return (
            db.query(self.model)
            .filter(self.model.student_id == student_id, self.model.qr_code_id == qr_code_id)
            .first()
        )
    
    def get_by_qr_code_id(self, db: Session, qr_code_id: str) -> Optional[Attendance]:
        return (
            db.query(self.model)
            .filter(self.model.qr_code_id == qr_code_id)
            .all()
        )
    
    def get_by_student_id(self, db: Session, student_id: str) -> Optional[Attendance]:
        return (
            db.query(self.model)
            .filter(self.model.student_id == student_id)
            .all()
        )

attendance_crud = AttendanceCRUD(Attendance)