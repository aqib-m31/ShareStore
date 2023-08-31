from django.conf import settings
import os
from datetime import datetime


def handle_uploaded_file(file, user_id):
    now = datetime.now()
    filename = f"{user_id}_{now.strftime('%Y%m%d%H%M%S')}_{file.name}"
    user_folder = f"user_{user_id}"
    file_path = os.path.join(settings.MEDIA_ROOT, user_folder, filename)

    if len(file_path) > 254:
        return False

    folder_path = os.path.join(settings.MEDIA_ROOT, user_folder)
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return file_path


def file_iterator(file, chunk_size=8192):
    with open(file, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
