from utils.db.base import ModelBase
from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON

class QRCode(ModelBase):
    name = Column(String, nullable=False)
    qr_code_data = Column(JSON, nullable=False)
    expiry_time = Column(TIMESTAMP, nullable=False)
    regenerate_interval_seconds = Column(Integer, default=1, nullable=False)
