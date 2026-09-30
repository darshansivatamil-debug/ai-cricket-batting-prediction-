import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.models import Video, Athlete
from backend.app.services.analysis_service import AnalysisPipelineService

# Create database tables
Base.metadata.create_all(bind=engine)

def test_end_to_end_pipeline():
    db = SessionLocal()
    try:
        video_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "sample_cover_drive.mp4")
        assert os.path.exists(video_path), f"Video file missing: {video_path}"

        # Register Video record
        video_rec = Video(
            filename="sample_cover_drive.mp4",
            filepath=video_path,
            duration=3.0,
            fps=30.0,
            resolution="1280x720"
        )
        db.add(video_rec)
        db.commit()
        db.refresh(video_rec)

        # Register Athlete record
        athlete = Athlete(name="Test University Athlete")
        db.add(athlete)
        db.commit()
        db.refresh(athlete)

        # Execute Pipeline
        service = AnalysisPipelineService()
        analysis = service.process_video_analysis(
            db=db,
            video_id=video_rec.id,
            athlete_id=athlete.id
        )

        print("=== END-TO-END PIPELINE TEST RESULTS ===")
        print(f"Status: {analysis.status}")
        print(f"Detected Shot: {analysis.shot_type} (Confidence: {analysis.confidence * 100:.1f}%)")
        print(f"Processing Time: {analysis.processing_time}s")
        print(f"Overlay Video URL: {analysis.overlay_video_url}")
        print("\nFeatures Calculated:")
        for feat in analysis.features:
            print(f"  - {feat.feature_name}: {feat.value} {feat.unit}")

        print("\nCoaching Feedback Generated:")
        for fb in analysis.feedbacks:
            print(f"  - [{fb.severity.upper()}] ({fb.category}): {fb.message}")

        assert analysis.status == "completed"
        assert analysis.shot_type != "Unknown"
        assert len(analysis.features) > 0
        assert len(analysis.feedbacks) > 0
        print("\nSuccess: End-to-End Analysis Pipeline verified!")

    finally:
        db.close()

if __name__ == "__main__":
    test_end_to_end_pipeline()
