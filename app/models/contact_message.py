from app.extensions import db, generate_uuid
from datetime import datetime

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactMessage {self.subject} from {self.email}>"
