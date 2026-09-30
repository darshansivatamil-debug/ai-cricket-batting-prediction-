import os
import time
import cv2
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.vision.video_processor import VideoProcessor, VideoProcessingError
from backend.app.vision.pose_detector import PoseDetector
from backend.app.vision.overlay_renderer import OverlayRenderer
from backend.app.analysis.biomechanics import BiomechanicsCalculator
from backend.app.analysis.technique_analyzer import TechniqueAnalyzer
from backend.app.analysis.feedback_engine import FeedbackEngine
from backend.app.ml.shot_classifier import ShotClassifier
from backend.app.models.models import Video, TrainingSession, Analysis, BiomechanicalFeature, Feedback

class AnalysisPipelineService:
    def __init__(self):
        self.shot_classifier = ShotClassifier()
        self.overlay_renderer = OverlayRenderer()

    def process_video_analysis(
        self,
        db: Session,
        video_id: str,
        athlete_id: str,
        shot_hint: Optional[str] = None
    ) -> Analysis:
        """
        Executes end-to-end video analysis pipeline and saves results to database.
        """
        start_time = time.time()
        
        # 1. Fetch Video record from database
        video_rec = db.query(Video).filter(Video.id == video_id).first()
        if not video_rec:
            raise VideoProcessingError(f"Video with id {video_id} not found in database.")

        # Create TrainingSession record
        session_rec = TrainingSession(
            athlete_id=athlete_id,
            video_id=video_id,
            title=f"Batting Analysis ({video_rec.filename})"
        )
        db.add(session_rec)
        db.commit()
        db.refresh(session_rec)

        # Create Analysis record (status: processing)
        analysis_rec = Analysis(
            session_id=session_rec.id,
            status="processing",
            shot_type="Analyzing...",
            confidence=0.0
        )
        db.add(analysis_rec)
        db.commit()
        db.refresh(analysis_rec)

        try:
            # 2. Inspect video metadata
            meta = VideoProcessor.inspect_video(video_rec.filepath)
            video_rec.duration = meta["duration"]
            video_rec.fps = meta["fps"]
            video_rec.resolution = meta["resolution"]

            # 3. Pose Detection & Biomechanical Extraction Loop
            pose_detector = PoseDetector()
            frame_metrics_list = []
            pose_data_list = []
            
            # Setup video writer for overlay output
            output_filename = f"overlay_{analysis_rec.id}.mp4"
            output_filepath = os.path.join(settings.OUTPUT_DIR, output_filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(output_filepath, fourcc, meta["fps"], (meta["width"], meta["height"]))

            frame_idx = 0
            for idx, timestamp, frame_bgr in VideoProcessor.extract_frames(video_rec.filepath):
                pose = pose_detector.process_frame(frame_bgr)
                pose_data_list.append(pose)

                if pose and "landmarks_normalized" in pose:
                    metrics = BiomechanicsCalculator.compute_frame_biomechanics(pose["landmarks_normalized"])
                    metrics["timestamp"] = timestamp
                    frame_metrics_list.append(metrics)

                frame_idx += 1

            pose_detector.close()

            if not frame_metrics_list:
                analysis_rec.status = "failed"
                analysis_rec.error_message = "No human player pose detected in the video. Please upload a clear cricket video with the player in frame."
                db.commit()
                out_writer.release()
                return analysis_rec

            # 4. Compute Temporal Biomechanical Summary
            metrics_summary = BiomechanicsCalculator.compute_temporal_summary(frame_metrics_list)

            # 5. Shot Classification
            shot_name, confidence = self.shot_classifier.classify_shot(
                frame_metrics_list=frame_metrics_list,
                metrics_summary=metrics_summary,
                user_hint=shot_hint
            )

            # 6. Technique Analysis
            observations = TechniqueAnalyzer.analyze_technique(
                shot_type=shot_name,
                metrics_summary=metrics_summary,
                frame_metrics=frame_metrics_list
            )

            # 7. Feedback Generation
            feedbacks_list = FeedbackEngine.generate_feedback(observations, shot_name)

            # 8. Render Pose Overlay Video & Write Frames
            # Second pass or reuse captured frames
            cap = cv2.VideoCapture(video_rec.filepath)
            f_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                pose = pose_data_list[f_count] if f_count < len(pose_data_list) else None
                key_angles = frame_metrics_list[min(f_count, len(frame_metrics_list)-1)] if frame_metrics_list else None

                annotated_frame = self.overlay_renderer.draw_pose_overlay(
                    frame_bgr=frame,
                    pose_data=pose,
                    shot_name=shot_name,
                    confidence=confidence,
                    key_angles=key_angles,
                    frame_number=f_count
                )
                out_writer.write(annotated_frame)
                f_count += 1

            cap.release()
            out_writer.release()

            # 9. Update Database Analysis Record
            processing_time = round(time.time() - start_time, 2)
            
            analysis_rec.status = "completed"
            analysis_rec.shot_type = shot_name
            analysis_rec.confidence = round(confidence, 2)
            analysis_rec.processing_time = processing_time
            analysis_rec.overlay_video_url = f"/api/videos/outputs/{output_filename}"

            # Save Biomechanical Features
            for name, val in metrics_summary.items():
                feat = BiomechanicalFeature(
                    analysis_id=analysis_rec.id,
                    feature_name=name,
                    value=float(val),
                    unit="deg" if "angle" in name or "inclination" in name else "ratio"
                )
                db.add(feat)

            # Save Feedbacks
            for fb in feedbacks_list:
                fb_rec = Feedback(
                    analysis_id=analysis_rec.id,
                    category=fb["category"],
                    severity=fb["severity"],
                    message=fb["message"],
                    confidence=fb["confidence"]
                )
                db.add(fb_rec)

            db.commit()
            db.refresh(analysis_rec)
            return analysis_rec

        except Exception as e:
            db.rollback()
            analysis_rec.status = "failed"
            analysis_rec.error_message = f"Processing failed: {str(e)}"
            db.commit()
            return analysis_rec
