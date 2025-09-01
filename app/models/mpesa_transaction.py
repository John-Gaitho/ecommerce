import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db, generate_uuid

class MpesaTransaction(db.Model):
    __tablename__ = "mpesa_transactions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checkout_request_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    account_reference = db.Column(db.String(255))
    result_code = db.Column(db.Integer)
    result_desc = db.Column(db.Text)
    mpesa_receipt_number = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, nullable=True)  # parsed from Safaricom
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default="pending")

    # ✅ Use UUID, not String
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    user = db.relationship("User", backref="mpesa_transactions")

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<MpesaTransaction {self.checkout_request_id} - {self.status}>"
