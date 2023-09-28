from fastapi import APIRouter, Depends, UploadFile, HTTPException
from dependencies import auth_service

file_router = APIRouter()
allowed_images_type = ["image/png", "image/gif", "image/jpeg", "image/jpg"]
allowed_video_type = ["video/mp4"]
all_allowed_file_types = []
all_allowed_file_types.extend(allowed_images_type)
all_allowed_file_types.extend(allowed_video_type)


@file_router.post(path="/upload")
async def upload_file(files: list[UploadFile]):
    for file in files:
        # Get the file size (in bytes)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        await file.seek(0)

        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large, must be less than 10Mb")

        content_type = file.content_type
        if content_type not in all_allowed_file_types:
            raise HTTPException(status_code=400, detail="Invalid file type")

    return "Ok"
