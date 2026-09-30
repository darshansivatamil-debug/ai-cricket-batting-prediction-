from typing import List, Optional
from pydantic import BaseModel, ConfigDict
import datetime

class BiomechanicalFeatureBase(BaseModel):
    feature_name: str
    value: float
    unit: Optional[str] = "deg"
    timestamp: Optional[float] = None

class BiomechanicalFeatureResponse(BiomechanicalFeatureBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    category: str
    severity: str
    message: str
    confidence: float

class FeedbackResponse(FeedbackBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class AnalysisStartRequest(BaseModel):
    video_id: str
    athlete_id: Optional[str] = None
    shot_type_hint: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: str
    session_id: str
    shot_type: str
    confidence: float
    status: str
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    overlay_video_url: Optional[str] = None
    features: List[BiomechanicalFeatureResponse] = []
    feedbacks: List[FeedbackResponse] = []
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    duration: float
    fps: float
    resolution: str
    message: str

class AthleteBase(BaseModel):
    name: str

class AthleteCreate(AthleteBase):
    pass

class AthleteResponse(AthleteBase):
    id: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class HistorySessionResponse(BaseModel):
    session_id: str
    analysis_id: str
    video_filename: str
    shot_type: str
    confidence: float
    created_at: datetime.datetime
    feedback_summary: List[str] = []
    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    pose_detector: str
