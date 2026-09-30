import os

class Settings:
    PROJECT_NAME: str = "AI-Powered Virtual Cricket Coach"
    API_V1_STR: str = "/api"
    
    # Base paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "outputs")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'cricket_coach.db')}")
    
    # Video constraints
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: set = {".mp4", ".mov", ".avi", ".mkv"}
    MIN_VIDEO_DURATION_SEC: float = 0.5
    MAX_VIDEO_DURATION_SEC: float = 60.0
    
    # AI / Model defaults
    CONFIDENCE_THRESHOLD: float = 0.50
    MIN_DETECTION_CONFIDENCE: float = 0.50
    MIN_TRACKING_CONFIDENCE: float = 0.50

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
