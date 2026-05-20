from flask import Blueprint, request, redirect, url_for, flash, current_app
from app.services.storage import StorageService

delete_bp = Blueprint("delete", __name__)

@delete_bp.route("/delete/<file_id>", methods=["POST"])
def delete_file(file_id):
    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    deleted = storage.delete(file_id)

    if deleted:
        flash("File deleted successfully.", "success")
    else:
        flash("File not found.", "error")

    return redirect(request.referrer or url_for("dashboard.index"))