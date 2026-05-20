from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
from app.services.storage import StorageService

upload_bp = Blueprint("upload", __name__)

ALLOWED_CATEGORIES = {"documents", "portfolio", "samples", "media"}

@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html", categories=ALLOWED_CATEGORIES)

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file in request"}), 400

    file     = request.files["file"]
    category = request.form.get("category", "documents")

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if category not in ALLOWED_CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    record  = storage.save(
        file_stream   = file.stream,
        original_name = file.filename,
        category      = category,
        ip            = request.remote_addr,
    )

    return jsonify({
        "message": "Upload successful",
        "file":    record.to_dict()
    }), 201