from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.storage import StorageService
from app.services.file_validator import FileValidator
from app.services.token_service import TokenService

upload_bp = Blueprint("upload", __name__)

ALLOWED_CATEGORIES = {"documents", "portfolio", "samples", "media"}

@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    token = request.args.get("t", "").strip()
    qr_token = ""
    qr_token_valid = False
    qr_token_error = None

    if token:
        token_service = TokenService(current_app.config["SECRET_KEY"])
        ok, result = token_service.verify_upload_token(token, max_age=600)

        if ok:
            qr_token = token
            qr_token_valid = True
        else:
            qr_token_error = result

    return render_template(
        "upload.html",
        categories=sorted(ALLOWED_CATEGORIES),
        qr_token=qr_token,
        qr_token_valid=qr_token_valid,
        qr_token_error=qr_token_error
    )

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file in request"}), 400

    file = request.files["file"]
    category = request.form.get("category", "documents").strip()
    qr_token = request.form.get("qr_token", "").strip()

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if category not in ALLOWED_CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    # If request came through QR access, token must still be valid at upload time
    if qr_token:
        token_service = TokenService(current_app.config["SECRET_KEY"])
        ok, result = token_service.verify_upload_token(qr_token, max_age=600)

        if not ok:
            return jsonify({"error": f"QR token {result}"}), 403

    validator = FileValidator(current_app.config["ALLOWED_EXTENSIONS"])
    is_valid, error = validator.validate(file.filename, category)

    if not is_valid:
        return jsonify({"error": error}), 400

    storage = StorageService(current_app.config["UPLOAD_ROOT"])
    record = storage.save(
        file_stream=file.stream,
        original_name=file.filename,
        category=category,
        ip=request.remote_addr,
    )

    return jsonify({
        "message": "Upload successful",
        "file": record.to_dict(),
        "qr_access": bool(qr_token)
    }), 201