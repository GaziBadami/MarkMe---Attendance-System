import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status

from src.user.crud import user_crud
from src.user.models import UserRoles
from src.user.schemas import (
    LoginRequest,
    Token,
    UserBase,
    UserRequest,
    UserResponse,
    UserUpdate,
    FacultyResponse,
    DashboardResponseSchema,
    RecentScanResponse,
)
from src.user.utils.deps import authenticated_user, is_authorized_for
from src.user.utils.smtp import send_email
from utils.db.session import get_db

from src.student.crud import student_crud
from src.attendance.crud import attendance_crud
from src.qr_code.crud import qr_code_crud


logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.post("/faculty/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_creds: LoginRequest, db: get_db):
    user = user_crud.get_by_email(db, login_creds.email)
    if not user or (not user.verify_password(login_creds.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return Token(user=user, token=user.create_token())


@user_router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(user_db: authenticated_user):
    user, _ = user_db
    return user


@user_router.get(
    "/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK
)
def get_users(
    user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])
):
    _, db = user_db

    return user_crud.get_multi(db)


@user_router.patch(
    "/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def update_user(user_req: UserUpdate, user_db: authenticated_user):
    user, db = user_db
    return user_crud.update(db, db_obj=user, obj_in=user_req)


@user_router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_db: authenticated_user):
    user, db = user_db
    user_crud.soft_del(db, db_obj=user)
    return None

# Faculty APIs
@user_router.post("/faculty/registration", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_faculty(user_req: UserRequest, user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    _, db = user_db

    if user_crud.get_by_email(db, user_req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    faculty_first_name = user_req.firstname.lower().strip().replace(" ", "").split(".")[-1]
    department = user_req.department.lower().strip().replace(".", "")
    password = faculty_first_name + "@" + department

    user_id = str(uuid.uuid4())
    user = user_crud.create(
        db,
        obj_in=UserBase(
            id=user_id, created_by=user_req.firstname, updated_by=user_req.lastname, password=password, **user_req.model_dump()
        ),
    )
    subject = "🎉 Welcome to MarkMe – Your GLS Faculty Account is Ready"
    user_info = {
        "firstname": user.firstname,
        "email": user.email,
        "password": password
    }
    send_email(user.email, subject, user_info,"faculty")
    return user

@user_router.get(
    "/faculties", response_model=List[FacultyResponse], status_code=status.HTTP_200_OK
)
def get_faculties(
    user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])
):
    _, db = user_db

    return user_crud.get_multi_faculty(db)

@user_router.patch(
    "/faculty/{faculty_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def update_user(faculty_id: str, faculty_req: UserUpdate, user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    _, db = user_db

    faculty = user_crud.get(db=db, id=faculty_id)
    if not faculty:
        raise HTTPException(detail="Faculty not found", status_code=status.HTTP_404_NOT_FOUND)

    return user_crud.update(db, db_obj=faculty, obj_in=faculty_req.model_dump(exclude_unset=True))

@user_router.get("/dashboard", status_code=status.HTTP_200_OK, response_model=DashboardResponseSchema)
def dashboard(user_db: is_authorized_for([UserRoles.ADMIN.value, UserRoles.SUPER_ADMIN.value])):
    try:
        user, db = user_db

        total_student = student_crud.get_all_student_count(db=db) or 0
        total_faculty = user_crud.get_all_faculty_count(db=db) or 0
        total_qr = qr_code_crud.get_all_qr_count(db=db) or 0
        total_scan = attendance_crud.get_all_attendance_count(db=db) or 0

        # TIP: support a small "limit" for latest scans in your CRUD (e.g., 10)
        recent_scan = attendance_crud.get_multi(db=db, per_page=10)

        recent_items: List[RecentScanResponse] = []
        for a in recent_scan:
            stu = getattr(a, "student", None)
            full_name = None
            roll_no = None
            enrollment_no = None
            if stu:
                first = getattr(stu, "first_name", "") or ""
                last = getattr(stu, "last_name", "") or ""
                full_name = (first + " " + last).strip() or None
                roll_no = getattr(stu, "roll_no", None)
                enrollment_no = getattr(stu, "enrollment_no", None)

            recent_items.append(
                RecentScanResponse(
                    fullname=full_name,
                    student_roll_no=roll_no,
                    student_enrollment=enrollment_no,
                    qr_code_id=a.qr_code_id,
                )
            )

        return DashboardResponseSchema(
            total_student=int(total_student),
            total_faculty=int(total_faculty),
            total_qr=int(total_qr),
            total_scan=int(total_scan),
            recent_scan=recent_items,
        )

    except Exception as e:
        logging.exception("===REASON===: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )
