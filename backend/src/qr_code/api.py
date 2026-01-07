import json
import qrcode
import logging

from typing import List
from io import BytesIO
from fastapi import APIRouter, status, HTTPException
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse

from src.user.models import UserRoles
from src.user.utils.deps import is_authorized_for
from src.qr_code.crud import qr_code_crud
from src.attendance.crud import attendance_crud
from src.student.crud import student_crud
from src.qr_code.schema import QrCodeBaseSchema, QrCodeRequestSchema, QrCodeUpdateSchema, QrCodeResponseSchema
from src.attendance.schemas import AttendanceResponseSchema

qr_code = APIRouter()

@qr_code.post("/generate/qr_code", status_code=status.HTTP_201_CREATED)
async def register_student_by_csv(
    request: QrCodeRequestSchema, user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])
):
    try:
        user, db = user_db
        # Current and end times
        start_time = datetime.now()
        end_time = request.expiry_time

        # Data to encode inside the QR
        data = {
            "name": request.name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "regenerate_interval_seconds": int(request.regenerate_interval_seconds),
        }

        qr_code = qr_code_crud.create(db=db, obj_in=QrCodeBaseSchema(
                name=request.name,
                qr_code_data=data,
                expiry_time=end_time,
                regenerate_interval_seconds=int(request.regenerate_interval_seconds),
                created_by=user.firstname + " " + user.lastname,
                updated_by=user.firstname + " " + user.lastname
            )
        )

        data["qr_code_id"] = qr_code.id

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json.dumps(data, separators=(",", ":")))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save image in memory
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # Return as image
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

@qr_code.get("/qr_code", response_model=List[QrCodeBaseSchema],status_code=status.HTTP_200_OK)
async def retrieve_students(user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    try:
        user, db = user_db

        students = qr_code_crud.get_multi(db)
        
        return students
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

@qr_code.get("/qr_code/{id}", response_model=QrCodeResponseSchema,status_code=status.HTTP_200_OK)
async def retrieve_students(id: str, user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    try:
        user, db = user_db

        qr_code = qr_code_crud.get(db, id)

        attendances = attendance_crud.get_by_qr_code_id(db=db, qr_code_id=qr_code.id)
        students = student_crud.get_all_student_count(db=db)

        attendance_data = []
        present_count = 0

        for a in attendances:
            attendance_data.append(
                AttendanceResponseSchema(
                    student_id=a.student_id,
                    student_first_name=a.student.first_name,
                    student_last_name=a.student.last_name,
                    student_roll_no=a.student.roll_no,
                    student_enrollment=a.student.enrollment_no,
                    attendance_time=a.attendance_time,
                    status=a.status,
                )
            )

            if str(a.status).lower() == "present":
                present_count += 1

        total_students = students if students else 0
        present_percentage = (present_count / total_students * 100) if total_students else 0

        qr_schema = QrCodeResponseSchema.model_validate(qr_code)
        qr_schema.attendance = attendance_data
        qr_schema.present_percentage = round(present_percentage, 2)
        qr_schema.total_students = total_students
        qr_schema.present_students = present_count

        return qr_schema
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )