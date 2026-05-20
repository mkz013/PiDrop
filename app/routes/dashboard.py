from flask import Blueprint, render_template, current_app
from app.extensions import db
from app.models.file_record import FileRecord
from app.services.storage import StorageService

dashboard_bp = Blueprint("dashboard", __name__)

CATEGORIES = ["documents", "portfolio", "samples", "media", "quarantine"]

@dashboard_bp.route("/")
def index():
    storage = StorageService(current_app.config["UPLOAD_ROOT"])

    # Stats per category
    stats = {}
    for cat in CATEGORIES:
        count = FileRecord.query.filter_by(category=cat).count()
        size  = db.session.query(db.func.sum(FileRecord.size_bytes))\
                          .filter_by(category=cat).scalar() or 0
        stats[cat] = {"count": count, "size": size}

    # 10 most recent uploads across all categories
    recent = FileRecord.query.order_by(FileRecord.uploaded_at.desc()).limit(10).all()

    total_size = storage.total_size()

    return render_template("dashboard.html",
                           stats=stats,
                           recent=recent,
                           total_size=total_size,
                           categories=CATEGORIES)