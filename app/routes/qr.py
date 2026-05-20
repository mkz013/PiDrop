from flask import Blueprint, render_template, request, send_file, current_app
from app.services.qr_service import QRService
from app.services.token_service import TokenService

qr_bp = Blueprint("qr", __name__)

@qr_bp.route("/qr")
def qr_page():
    host = request.host.split(":")[0]
    scheme = "http"

    token_service = TokenService(current_app.config["SECRET_KEY"])
    token = token_service.generate_upload_token()

    upload_url = f"{scheme}://{host}:1131/upload?t={token}"
    return render_template("qr.html", upload_url=upload_url)

@qr_bp.route("/qr-image")
def qr_image():
    host = request.host.split(":")[0]
    scheme = "http"

    token_service = TokenService(current_app.config["SECRET_KEY"])
    token = token_service.generate_upload_token()

    upload_url = f"{scheme}://{host}:1131/upload?t={token}"

    qr_service = QRService()
    img = qr_service.generate_png(upload_url)

    return send_file(img, mimetype="image/png")