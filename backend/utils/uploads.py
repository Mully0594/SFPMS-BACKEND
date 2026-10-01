import os
import uuid

from flask import current_app


def allowed_file(filename):
    """Check the file extension against the configured allow-list."""

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage, subfolder):
    """
    Save an uploaded werkzeug FileStorage object to
    UPLOAD_FOLDER/<subfolder>/ using a randomised filename, and return
    the relative path that should be stored in the database.

    Returns None if no file was provided.
    """

    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError(
            "Unsupported file type: " + file_storage.filename
        )

    extension = file_storage.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{extension}"

    folder_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        subfolder
    )

    os.makedirs(folder_path, exist_ok=True)

    file_storage.save(os.path.join(folder_path, unique_name))

    # Relative path used both for DB storage and for building the
    # public /uploads/<...> URL.
    return f"{subfolder}/{unique_name}"
