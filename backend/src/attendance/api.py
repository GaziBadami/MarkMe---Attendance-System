import logging
from datetime import date
from typing import List
from fastapi import APIRouter, status, HTTPException

from src.user.models import UserRoles
from src.user.utils.deps import is_authorized_for
from src.attendance.crud import attendance_crud
from src.attendance.enums import AttendanceEnum
from src.attendance.schemas import AttendanceBaseSchema, AttendanceRequestSchema
from utils.db.session import get_db

attendance_router = APIRouter()

@attendance_router.post("/attendance", status_code=status.HTTP_201_CREATED, response_model=AttendanceBaseSchema)
def create_attendance(request: AttendanceRequestSchema, db: get_db):
    try:
        # user, db = user_db
        
        is_exist = attendance_crud.get_by_user_and_qr_id(db=db, student_id=request.student_id, qr_code_id=request.qr_code_id)
        if is_exist:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Already present")

        attendance = attendance_crud.create(db=db, obj_in=AttendanceBaseSchema(created_by="dhruv", updated_by="dhruv", status=AttendanceEnum.PRESENT.value, **request.model_dump(exclude_unset=True)))
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

@attendance_router.get("/student/{student_id}/attendance", status_code=status.HTTP_201_CREATED, response_model=List[AttendanceBaseSchema])
def retrieve_by_student_id(student_id: str, user_db: is_authorized_for([UserRoles.STUDENT.value, UserRoles.SUPER_ADMIN.value])):
    try:
        _, db = user_db
        attendance = attendance_crud.get_by_student_id(db=db, student_id=student_id)

        # Sort by created_at (latest first)
        attendance.sort(key=lambda x: x.created_at, reverse=True)

        today = date.today()
        yesterday = today.fromordinal(today.toordinal() - 1)

        formatted_data = []

        for record in attendance:
            created_date = record.created_at.date()

            if created_date == today:
                day_label = "Today"
            elif created_date == yesterday:
                day_label = "Yesterday"
            else:
                day_label = created_date.strftime("%d %b %Y")  # Example: 13 Oct 2025

            record_dict = record.__dict__
            record_dict["day_label"] = day_label

            formatted_data.append(record_dict)

        return formatted_data

    except HTTPException:
        raise
    except Exception as e:
        raise e
