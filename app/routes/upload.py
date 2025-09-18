# app/routes/upload.py
import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

# ✅ Configure Cloudinary securely from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@upload_bp.route("/files", methods=["POST"])
@jwt_required()
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    try:
        result = cloudinary.uploader.upload(file, folder="branded-in-grace/uploads")
        return jsonify({
            "url": result["secure_url"],   # ✅ CDN URL to use in frontend
            "public_id": result["public_id"]
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
