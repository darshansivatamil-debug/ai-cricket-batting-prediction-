import os
import cv2
from typing import Dict, Any, Generator, Tuple

class VideoProcessingError(Exception):
    pass

class VideoProcessor:
    @staticmethod
    def inspect_video(filepath: str) -> Dict[str, Any]:
        """Loads video and returns metadata or raises error if invalid."""
        if not os.path.exists(filepath):
            raise VideoProcessingError(f"Video file does not exist: {filepath}")
        
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            raise VideoProcessingError("Uploaded file is empty (0 bytes).")
            
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise VideoProcessingError("Could not open video file. Format may be unsupported or corrupted.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()

        if frame_count <= 0 or fps <= 0 or width <= 0 or height <= 0:
            raise VideoProcessingError("Invalid video streams (frame count, FPS or resolution is 0).")

        duration = frame_count / fps

        if duration < 0.3:
            raise VideoProcessingError(f"Video duration is too short ({duration:.2f}s). Minimum 0.5s required.")
            
        if duration > 120.0:
            raise VideoProcessingError(f"Video duration ({duration:.1f}s) exceeds maximum allowed threshold of 120 seconds.")

        return {
            "filepath": filepath,
            "duration": round(duration, 2),
            "fps": round(fps, 2),
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "frame_count": frame_count
        }

    @staticmethod
    def extract_frames(filepath: str, sample_fps: float = None) -> Generator[Tuple[int, float, Any], None, None]:
        """Yields (frame_index, timestamp_sec, frame_bgr) from video."""
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise VideoProcessingError("Failed to open video for frame extraction.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        step = 1
        if sample_fps and sample_fps < fps:
            step = int(round(fps / sample_fps))
            if step < 1:
                step = 1

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if frame_idx % step == 0:
                timestamp = frame_idx / fps
                yield (frame_idx, timestamp, frame)

            frame_idx += 1

        cap.release()
