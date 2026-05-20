from flask import Blueprint, render_template, abort
from app.models.file_record import FileRecord

browser_bp = Blueprint("browser", __name__)

ALLOWED_CATEGORIES = {"documents", "portfolio", "samples", "media", "quarantine"}

@browser_bp.route("/files/<category>")
def browse_category(category):
    if category not in ALLOWED_CATEGORIES:
        abort(404)

    files = FileRecord.query.filter_by(category=category) \
                            .order_by(FileRecord.uploaded_at.desc()) \
                            .all()

    return render_template(
        "browser.html",
        category=category,
        files=files,
        categories=sorted(ALLOWED_CATEGORIES)
    )