from sqlalchemy.orm import Session
from src.student.models import Student
from src.student.schemas import StudentBase, StudentUpdate
from fastapi.encoders import jsonable_encoder

from utils.crud.base import CRUDBase

class StudentCRUD(CRUDBase[Student, StudentBase, StudentUpdate]):
    def get_by_enrollment(self, db: Session, enrollment_no: str) -> Student:
        return db.query(Student).filter(self.model.enrollment_no == enrollment_no).first()
    
    def register_student(self, db: Session, *, obj_in: StudentBase) -> Student:
        obj_in_data: dict = jsonable_encoder(obj_in)
        password = obj_in_data.pop("password", None)
        db_obj = self.model(**obj_in_data)
        if password:
            db_obj.set_password(password)
        db.add(db_obj)
        db.commit()
        return db_obj
    
    def get_all_student_count(self, db: Session):
        return db.query(Student).count()

student_crud = StudentCRUD(Student)