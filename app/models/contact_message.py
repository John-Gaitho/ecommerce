from app.extensions import db, generate_uuid
from datetime import datetime

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="unread")  # NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<ContactMessage {self.subject} from {self.email}>"
