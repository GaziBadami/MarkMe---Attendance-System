from enum import Enum
from datetime import datetime, timedelta
import jwt
from passlib.hash import pbkdf2_sha256
from src.config import Config
from src.user.schemas import UserRoles

from sqlalchemy import Column, String, Boolean

from utils.db.base import ModelBase

class Student(ModelBase):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    enrollment_no = Column(String, nullable=False)
    roll_no = Column(String, nullable=False)
    course = Column(String, nullable=False)
    div = Column(String, nullable=False)
    
    email = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)

    password = Column(String, nullable=False)

    def set_password(self, password):
        """Hash a password for storing."""
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, provided_password):
        """Verify a stored password against one provided by user"""
        return pbkdf2_sha256.verify(provided_password, self.password)

    def create_token(self):
        return jwt.encode(
            {
                "id": self.id,
                "email": self.email,
                "role": UserRoles.STUDENT.value,
                "exp": (
                    datetime.utcnow()
                    + timedelta(seconds=int(Config.JWT_EXPIRATION_TIME))
                ).timestamp(),
            },
            key=Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM,
        )