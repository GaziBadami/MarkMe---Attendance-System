import datetime
from utils.db.base import ModelBase
from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, ForeignKey, text, DateTime
from sqlalchemy.orm import relationship

class Attendance(ModelBase):
    student_id = Column(String, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    qr_code_id = Column(String, ForeignKey("qr_code.id", ondelete="CASCADE"), nullable=False)
    attendance_time = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, nullable=False)

    student = relationship("Student", uselist=False)
    qr_code = relationship("QRCode", uselist=False)

    @property
    def qr_code_name(self):
        return self.qr_code.name if self.qr_code else None
