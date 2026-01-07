import csv
import io
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, UploadFile

from src.student.schemas import StudentBase, StudentUpdate, StudentToken, StudentLoginRequest
from src.user.utils.smtp import send_email
from src.user.utils.deps import is_authorized_for
from src.user.models import UserRoles
from src.student.crud import student_crud
from utils.db.session import get_db


logger = logging.getLogger(__name__)

student_router = APIRouter()

@student_router.post("/register/student/csv", status_code=status.HTTP_201_CREATED)
async def register_student_by_csv(
    file: UploadFile, user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])
):
    try:
        user, db = user_db
        if not file:
            raise HTTPException(detail="File not found", status_code=status.HTTP_404_NOT_FOUND)
        
        # Step 1: Read file content
        content = await file.read()

        # Step 2: Convert bytes to string
        decoded_content = content.decode("utf-8")

        # Step 3: Use csv reader
        csv_reader = csv.DictReader(io.StringIO(decoded_content))

        # Step 4: Loop and print data
        for row in csv_reader:
            update_data = StudentUpdate(first_name=row["first_name"],last_name=row["last_name"],enrollment_no=row["enrollment_no"],roll_no=row["roll_no"],course=row["course"],div=row["div"],email=row["email"],phone_number=row["phone_number"])

            student_first_name = update_data.first_name.lower().strip().replace(" ", "").split(".")[-1]
            enroll_number = update_data.enrollment_no[-3::].strip()
            password = student_first_name + "@" + enroll_number

            data = StudentBase(password=password, created_by=user.firstname + " " + user.lastname, updated_by=user.firstname + " " + user.lastname, **update_data.model_dump())
            student_crud.register_student(db=db, obj_in=data)

            subject = "🎓 Welcome to MarkMe – Your GLS Student Account is Ready"
            user_info = {
                "firstname": update_data.first_name,
                "email": update_data.enrollment_no,
                "password": password
            }
            send_email(update_data.email, subject, user_info, "student" )
        
        return True
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

@student_router.get("/students", response_model=List[StudentBase],status_code=status.HTTP_200_OK)
async def retrieve_students(user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    try:
        user, db = user_db

        students = student_crud.get_multi(db)
        
        return students
    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

@student_router.post("/student/login", response_model=StudentToken, status_code=status.HTTP_200_OK)
def login(login_creds: StudentLoginRequest, db: get_db):
    student = student_crud.get_by_enrollment(db, login_creds.enrollment_no)
    if not student or (not student.verify_password(login_creds.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return StudentToken(user=student, token=student.create_token())