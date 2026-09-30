from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Athlete, TrainingSession, Analysis, Video
from backend.app.models.schemas import AthleteResponse, AthleteCreate, HistorySessionResponse

router = APIRouter(prefix="/athletes", tags=["Athletes"])

@router.post("/", response_model=AthleteResponse)
def create_athlete(athlete_in: AthleteCreate, db: Session = Depends(get_db)):
    athlete = Athlete(name=athlete_in.name)
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete

@router.get("/", response_model=List[AthleteResponse])
def list_athletes(db: Session = Depends(get_db)):
    athletes = db.query(Athlete).all()
    if not athletes:
        default_a = Athlete(name="University Batter")
        db.add(default_a)
        db.commit()
        db.refresh(default_a)
        athletes = [default_a]
    return athletes

@router.get("/{athlete_id}/history", response_model=List[HistorySessionResponse])
def get_athlete_history(athlete_id: str, db: Session = Depends(get_db)):
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found.")

    sessions = db.query(TrainingSession).filter(TrainingSession.athlete_id == athlete_id).all()
    history = []
    for s in sessions:
        an = db.query(Analysis).filter(Analysis.session_id == s.id).order_by(Analysis.created_at.desc()).first()
        v = db.query(Video).filter(Video.id == s.video_id).first()
        if an:
            feedback_msgs = [f.message for f in an.feedbacks[:2]]
            history.append(HistorySessionResponse(
                session_id=s.id,
                analysis_id=an.id,
                video_filename=v.filename if v else "unknown.mp4",
                shot_type=an.shot_type,
                confidence=an.confidence,
                created_at=an.created_at,
                feedback_summary=feedback_msgs
            ))
    return history
