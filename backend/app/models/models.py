import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, default="Default Athlete")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("TrainingSession", back_populates="athlete", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    duration = Column(Float, nullable=True)
    fps = Column(Float, nullable=True)
    resolution = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("TrainingSession", back_populates="video", cascade="all, delete-orphan")

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    athlete_id = Column(String(36), ForeignKey("athletes.id"), nullable=False)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    title = Column(String(200), default="Batting Analysis Session")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    athlete = relationship("Athlete", back_populates="sessions")
    video = relationship("Video", back_populates="sessions")
    analyses = relationship("Analysis", back_populates="session", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("training_sessions.id"), nullable=False)
    shot_type = Column(String(100), nullable=False, default="Unknown")
    confidence = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    overlay_video_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("TrainingSession", back_populates="analyses")
    features = relationship("BiomechanicalFeature", back_populates="analysis", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="analysis", cascade="all, delete-orphan")

class BiomechanicalFeature(Base):
    __tablename__ = "biomechanical_features"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    feature_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True, default="deg")
    timestamp = Column(Float, nullable=True)

    analysis = relationship("Analysis", back_populates="features")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, default="info") # info, low, moderate, high
    message = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="feedbacks")
