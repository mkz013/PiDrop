import uuid
from datetime import datetime
from app.extensions import db

class FileRecord(db.Model):
    __tablename__ = "file_records"

    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename    = db.Column(db.String(255), nullable=False)   # sanitized original name
    stored_as   = db.Column(db.String(36),  nullable=False)   # UUID name on disk
    category    = db.Column(db.String(50),  nullable=False)   # documents/portfolio/etc
    mime_type   = db.Column(db.String(100), nullable=True)
    size_bytes  = db.Column(db.Integer,     nullable=False)
    sha256      = db.Column(db.String(64),  nullable=True)
    uploaded_at = db.Column(db.DateTime,    default=datetime.utcnow)
    uploaded_ip = db.Column(db.String(45),  nullable=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "filename":    self.filename,
            "category":    self.category,
            "mime_type":   self.mime_type,
            "size_bytes":  self.size_bytes,
            "sha256":      self.sha256,
            "uploaded_at": self.uploaded_at.isoformat(),
            "uploaded_ip": self.uploaded_ip,
        }
    
    def full_path(self, upload_root):
        import os
        return os.path.join(upload_root, self.category, self.stored_as)

    def __repr__(self):
        return f"<FileRecord {self.filename} [{self.category}]>"