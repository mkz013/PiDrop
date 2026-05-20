import os
import mimetypes
import markdown
import bleach

from flask import Blueprint, abort, current_app, render_template, send_file
from app.services.storage import StorageService

view_bp = Blueprint("view", __name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}
TEXT_EXTENSIONS = {".txt", ".md"}
PDF_EXTENSIONS = {".pdf"}

BLOCKED_INLINE_EXTENSIONS = {
    ".js", ".py", ".sh", ".ps1", ".bat", ".cmd",
    ".exe", ".dll", ".bin", ".apk", ".jar",
    ".html", ".hta", ".vbs", ".iso"
}

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "strong", "em", "b", "i", "code", "pre", "blockquote",
    "ul", "ol", "li",
    "a",
    "table", "thead", "tbody", "tr", "th", "td"
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
}

@view_bp.route("/view/<file_id>", methods=["GET"])
def view_file(file_id):
    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    record = storage.get(file_id)

    if not record:
        abort(404)

    if record.category == "samples":
        abort(403)

    file_path = storage.resolve_path(record)
    _, ext = os.path.splitext(record.filename)
    ext = ext.lower()

    if ext in BLOCKED_INLINE_EXTENSIONS:
        abort(403)

    prev_id, next_id = storage.media_neighbors(record.id, record.category)

    if ext in IMAGE_EXTENSIONS:
        return render_template(
            "view_media.html",
            file=record,
            media_type="image",
            prev_id=prev_id,
            next_id=next_id
        )

    if ext in VIDEO_EXTENSIONS:
        return render_template(
            "view_media.html",
            file=record,
            media_type="video",
            prev_id=prev_id,
            next_id=next_id
        )

    if ext in PDF_EXTENSIONS:
        return render_template(
            "view_pdf.html",
            file=record,
            prev_id=prev_id,
            next_id=next_id
        )

    if ext in TEXT_EXTENSIONS:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        if ext == ".md":
            rendered = markdown.markdown(raw_text, extensions=["fenced_code", "tables"])
            safe_html = bleach.clean(
                rendered,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                protocols=["http", "https", "mailto"],
                strip=True
            )
            return render_template(
                "view_markdown.html",
                file=record,
                rendered_html=safe_html,
                is_markdown=True,
                prev_id=prev_id,
                next_id=next_id
            )

        safe_text = bleach.clean(raw_text)
        safe_html = "<pre style='white-space:pre-wrap; word-break:break-word; margin:0;'>" + safe_text + "</pre>"
        return render_template(
            "view_markdown.html",
            file=record,
            rendered_html=safe_html,
            is_markdown=False,
            prev_id=prev_id,
            next_id=next_id
        )

    abort(403)

@view_bp.route("/view-raw/<file_id>", methods=["GET"])
def view_raw_file(file_id):
    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    record = storage.get(file_id)

    if not record:
        abort(404)

    if record.category == "samples":
        abort(403)

    _, ext = os.path.splitext(record.filename)
    ext = ext.lower()

    allowed = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | PDF_EXTENSIONS
    if ext not in allowed:
        abort(403)

    file_path = storage.resolve_path(record)
    mime_type, _ = mimetypes.guess_type(record.filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    response = send_file(
        file_path,
        mimetype=mime_type,
        as_attachment=False,
        download_name=record.filename
    )
    response.headers["Content-Disposition"] = f'inline; filename="{record.filename}"'
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response