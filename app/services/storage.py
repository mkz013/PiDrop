import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import func

from app.extensions import db
from app.models.file_record import FileRecord


class StorageService:
    def __init__(self, upload_root):
        self.upload_root = upload_root

    def _category_dir(self, category):
        path = os.path.join(self.upload_root, category)
        os.makedirs(path, exist_ok=True)
        return path

    def save(self, file_stream, original_name, category, ip=None):
        safe_name = secure_filename(original_name)
        ext = os.path.splitext(safe_name)[1].lower()
        file_id = str(uuid.uuid4())
        stored_as = f"{file_id}{ext}"

        category_dir = self._category_dir(category)
        file_path = os.path.join(category_dir, stored_as)

        data = file_stream.read()
        with open(file_path, "wb") as f:
            f.write(data)

        record = FileRecord(
            id=file_id,
            filename=safe_name,
            stored_as=stored_as,
            category=category,
            size_bytes=len(data),
            uploaded_at=datetime.utcnow(),
            uploaded_ip=ip,
        )

        db.session.add(record)
        db.session.commit()
        return record

    def list_by_category(self, category):
        return (
            FileRecord.query
            .filter_by(category=category)
            .order_by(FileRecord.uploaded_at.desc())
            .all()
        )

    def recent_files(self, limit=10):
        return (
            FileRecord.query
            .order_by(FileRecord.uploaded_at.desc())
            .limit(limit)
            .all()
        )

    def get(self, file_id):
        return FileRecord.query.filter_by(id=file_id).first()

    def resolve_path(self, record):
        return os.path.join(self.upload_root, record.category, record.stored_as)

    def total_size(self):
        total = db.session.query(func.coalesce(func.sum(FileRecord.size_bytes), 0)).scalar()
        return int(total or 0)

    def total_files(self):
        return db.session.query(func.count(FileRecord.id)).scalar() or 0

    def category_counts(self):
        rows = (
            db.session.query(FileRecord.category, func.count(FileRecord.id))
            .group_by(FileRecord.category)
            .all()
        )
        return {category: count for category, count in rows}

    def media_neighbors(self, file_id, category):
        files = (
            FileRecord.query
            .filter_by(category=category)
            .order_by(FileRecord.uploaded_at.desc())
            .all()
        )

        ids = [f.id for f in files]
        if file_id not in ids:
            return None, None

        idx = ids.index(file_id)
        prev_id = ids[idx - 1] if idx > 0 else None
        next_id = ids[idx + 1] if idx < len(ids) - 1 else None
        return prev_id, next_id

    def delete(self, file_id):
        record = self.get(file_id)
        if not record:
            return False

        file_path = self.resolve_path(record)

        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(record)
        db.session.commit()
        return True