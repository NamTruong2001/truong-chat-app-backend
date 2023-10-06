from fastapi import UploadFile
from .exceptions import FileTooLargeException, InvalidFileType, FilenameTooLong

allowed_images_type = ["image/png", "image/gif", "image/jpeg", "image/jpg"]
allowed_video_type = ["video/mp4"]
all_allowed_file_types = []
all_allowed_file_types.extend(allowed_images_type)
all_allowed_file_types.extend(allowed_video_type)
async def validate_upload_file_to_azure_blob_service(file: UploadFile):

    if len(file.filename) > 50:
        raise FilenameTooLong(message="File name too must less than <= 50")

    if file.content_type not in all_allowed_file_types:
        raise InvalidFileType(message="Invalid file type")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)

    if file_size > 10 * 1024 * 1024:
        raise FileTooLargeException(message="File too large, must be less than 10Mb")