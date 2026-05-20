import os
from flask import Blueprint, current_app, abort, send_file
from app.services.storage import StorageService

download_bp = Blueprint("download", __name__)

@download_bp.route("/dl/<file_id>")
def download_file(file_id):
    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    record = storage.get(file_id)

    if not record:
        abort(404)

    path = record.full_path(current_app.config["UPLOAD_ROOT"])

    if not os.path.isfile(path):
        abort(404)

    return send_file(
        path,
        as_attachment=True,
        download_name=record.filename
    )