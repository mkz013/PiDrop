import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.file_record import FileRecord

class StorageService:

    def __init__(self, upload_root):
        self.upload_root = upload_root

    def save(self, file_stream, original_name, category, ip=None):
        """
        Sanitize filename, generate UUID storage name,
        compute SHA256, write to disk, persist to DB.
        Returns the FileRecord.
        """
        safe_name  = secure_filename(original_name)
        stored_as  = str(uuid.uuid4())
        dest_dir   = os.path.join(self.upload_root, category)
        dest_path  = os.path.join(dest_dir, stored_as)

        os.makedirs(dest_dir, exist_ok=True)

        # Write file and compute hash in one pass
        sha256 = hashlib.sha256()
        size   = 0
        with open(dest_path, "wb") as f:
            while chunk := file_stream.read(8192):
                f.write(chunk)
                sha256.update(chunk)
                size += len(chunk)

        record = FileRecord(
            filename    = safe_name,
            stored_as   = stored_as,
            category    = category,
            size_bytes  = size,
            sha256      = sha256.hexdigest(),
            uploaded_ip = ip,
        )
        db.session.add(record)
        db.session.commit()
        return record

    def list_category(self, category):
        return FileRecord.query.filter_by(category=category)\
                               .order_by(FileRecord.uploaded_at.desc()).all()

    def get(self, file_id):
        return FileRecord.query.get(file_id)

    def delete(self, file_id):
        record = self.get(file_id)
        if not record:
            return False
        path = record.full_path(self.upload_root)
        if os.path.exists(path):
            os.remove(path)
        db.session.delete(record)
        db.session.commit()
        return True

    def total_size(self):
        result = db.session.query(db.func.sum(FileRecord.size_bytes)).scalar()
        return result or 0