import os
from uuid import uuid4
from PIL import Image
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.utils.jwt_utils import roles_required

upload_bp = Blueprint("upload", __name__)

@upload_bp.post("/product-images")
@jwt_required()
@roles_required("admin","owner")
def upload_image():
    if "file" not in request.files:
        return jsonify({"message":"file required"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"message":"invalid filename"}), 400

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    ext = os.path.splitext(f.filename)[1].lower()
    name = f"{uuid4().hex}{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    f.save(path)

    # optimize (resize if too big)
    try:
        with Image.open(path) as img:
            img.thumbnail((1600, 1600))
            img.save(path, optimize=True, quality=85)
    except Exception:
        pass

    url = f"/uploads/{name}"
    return jsonify({"url": url})
