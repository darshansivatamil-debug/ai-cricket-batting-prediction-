import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.models import Video
from backend.app.models.schemas import VideoUploadResponse
from backend.app.vision.video_processor import VideoProcessor, VideoProcessingError

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Validates uploaded cricket video file, saves to upload storage, and registers video record.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename uploaded.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Generate secure unique file name
    file_id = str(uuid.uuid4())
    saved_filename = f"{file_id}{ext}"
    saved_filepath = os.path.join(settings.UPLOAD_DIR, saved_filename)

    # Write contents safely
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum upload limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    with open(saved_filepath, "wb") as f:
        f.write(contents)

    # Inspect video with OpenCV
    try:
        meta = VideoProcessor.inspect_video(saved_filepath)
    except VideoProcessingError as e:
        if os.path.exists(saved_filepath):
            os.remove(saved_filepath)
        raise HTTPException(status_code=400, detail=str(e))

    # Save record to Database
    video_rec = Video(
        id=file_id,
        filename=file.filename,
        filepath=saved_filepath,
        duration=meta["duration"],
        fps=meta["fps"],
        resolution=meta["resolution"]
    )
    db.add(video_rec)
    db.commit()
    db.refresh(video_rec)

    return VideoUploadResponse(
        video_id=video_rec.id,
        filename=video_rec.filename,
        duration=video_rec.duration,
        fps=video_rec.fps,
        resolution=video_rec.resolution,
        message="Video uploaded and validated successfully."
    )

@router.get("/uploads/{filename}")
def serve_upload_video(filename: str):
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Requested video file not found.")
    return FileResponse(filepath, media_type="video/mp4")

@router.get("/outputs/{filename}")
def serve_output_video(filename: str):
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Requested analysis video not found.")
    return FileResponse(filepath, media_type="video/mp4")
