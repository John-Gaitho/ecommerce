# app/utils/file_upload.py
import os
import uuid
from werkzeug.utils import secure_filename
from app.config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder=""):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        folder = os.path.join(Config.UPLOAD_FOLDER, subfolder)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, unique_name)
        file.save(filepath)

        # ✅ store relative path
        rel_path = os.path.join(subfolder, unique_name).replace("\\", "/")
        return f"/uploads/{rel_path}"
    return None
def delete_file(file_path):
    if file_path.startswith("/uploads/"):
        file_path = file_path[len("/uploads/"):]
    full_path = os.path.join(Config.UPLOAD_FOLDER, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False
def get_file_url(file_path):
    if file_path.startswith("/uploads/"):
        return file_path
    return f"/uploads/{file_path}"
def get_file_path(file_url):
    if file_url.startswith("/uploads/"):
        return file_url[len("/uploads/"):]
    return file_url
