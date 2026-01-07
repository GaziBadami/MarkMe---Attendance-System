from sqlalchemy.orm import Session

from src.qr_code.models import QRCode
from src.qr_code.schema import QrCodeBaseSchema, QrCodeUpdateSchema

from utils.crud.base import CRUDBase

class QrCodeCRUD(CRUDBase[QRCode, QrCodeBaseSchema, QrCodeUpdateSchema]):
    def get_all_qr_count(self, db: Session):
        return db.query(QRCode).count()

qr_code_crud = QrCodeCRUD(QRCode)