# app/routes/upload.py
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

# ✅ Ensure upload folder exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Serve uploaded files ---
@upload_bp.route("/files/<filename>")
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# --- Product image upload ---
@upload_bp.route("/product-images", methods=["POST"])
def upload_product_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # ✅ Return full URL (accessible directly)
    file_url = f"{request.host_url}api/upload/files/{filename}"

    return jsonify({"url": file_url, "filename": filename}), 201
