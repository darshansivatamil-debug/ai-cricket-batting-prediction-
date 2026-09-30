from fastapi import APIRouter
from backend.app.models.schemas import HealthResponse
from backend.app.ml.evaluator import ModelEvaluator

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    eval_res = ModelEvaluator.evaluate_model()
    return HealthResponse(
        status="ok",
        version="1.0.0-academic-prototype",
        models_loaded=True,
        pose_detector="MediaPipe Pose Landmarker 3D"
    )

@router.get("/evaluation")
def get_model_evaluation():
    return ModelEvaluator.evaluate_model()
