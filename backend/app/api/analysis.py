from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Analysis, Video, Athlete
from backend.app.models.schemas import AnalysisStartRequest, AnalysisResponse
from backend.app.services.analysis_service import AnalysisPipelineService

router = APIRouter(prefix="/analysis", tags=["Analysis"])
pipeline_service = AnalysisPipelineService()

@router.post("/start", response_model=AnalysisResponse)
def start_analysis(
    req: AnalysisStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Triggers analysis process for an uploaded video.
    """
    video_rec = db.query(Video).filter(Video.id == req.video_id).first()
    if not video_rec:
        raise HTTPException(status_code=404, detail=f"Video ID '{req.video_id}' not found.")

    # Get or create default athlete if not supplied
    athlete_id = req.athlete_id
    if not athlete_id:
        default_athlete = db.query(Athlete).first()
        if not default_athlete:
            default_athlete = Athlete(name="University Athlete")
            db.add(default_athlete)
            db.commit()
            db.refresh(default_athlete)
        athlete_id = default_athlete.id

    # Execute analysis synchronously or via background task
    # For reliable REST response, execute pipeline directly
    analysis_rec = pipeline_service.process_video_analysis(
        db=db,
        video_id=video_rec.id,
        athlete_id=athlete_id,
        shot_hint=req.shot_type_hint
    )

    return analysis_rec

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    analysis_rec = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis_rec:
        raise HTTPException(status_code=404, detail=f"Analysis ID '{analysis_id}' not found.")
    return analysis_rec

@router.get("/{analysis_id}/results", response_model=AnalysisResponse)
def get_analysis_results(analysis_id: str, db: Session = Depends(get_db)):
    analysis_rec = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis_rec:
        raise HTTPException(status_code=404, detail=f"Analysis ID '{analysis_id}' not found.")
    return analysis_rec
