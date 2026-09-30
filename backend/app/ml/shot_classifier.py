import os
import pickle
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

SUPPORTED_SHOTS = [
    "Forward Defence",
    "Straight Drive",
    "Cover Drive",
    "Pull Shot",
    "Cut Shot"
]

class ShotClassifier:
    """
    Modular Shot Classification engine.
    Supports baseline rule-based classification and classical ML (Random Forest/SVM) models.
    Returns 'Shot classification uncertain' if prediction confidence < confidence_threshold.
    """
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold
        self.ml_model = None
        self.is_ml_loaded = False
        
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                self.is_ml_loaded = True
            except Exception as e:
                print(f"Warning: Failed to load ML model from {model_path}: {e}")

    def classify_shot(
        self,
        frame_metrics_list: List[Dict[str, float]],
        metrics_summary: Dict[str, float],
        user_hint: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Classifies cricket shot type from temporal biomechanical feature sequence.
        Returns: (shot_name, confidence_score)
        """
        if user_hint and user_hint in SUPPORTED_SHOTS:
            return user_hint, 0.95

        if not frame_metrics_list:
            return "Shot classification uncertain", 0.0

        # If trained ML model is available, use feature vector prediction
        if self.is_ml_loaded and self.ml_model is not None:
            feature_vector = self._extract_feature_vector(frame_metrics_list, metrics_summary)
            try:
                probs = self.ml_model.predict_proba([feature_vector])[0]
                max_idx = int(np.argmax(probs))
                max_conf = float(probs[max_idx])
                predicted_shot = self.ml_model.classes_[max_idx]

                if max_conf < self.confidence_threshold:
                    return "Shot classification uncertain", max_conf
                return predicted_shot, max_conf
            except Exception as e:
                print(f"ML prediction error: {e}, falling back to rule-based classifier.")

        # Fallback to Rule-based / Heuristic Temporal Classifier
        return self._rule_based_classify(frame_metrics_list, metrics_summary)

    def _rule_based_classify(
        self,
        frame_metrics: List[Dict[str, float]],
        metrics_summary: Dict[str, float]
    ) -> Tuple[str, float]:
        """
        Heuristic classification based on trunk inclination, knee flexion, and arm extension.
        """
        avg_trunk = metrics_summary.get("avg_trunk_inclination", 0.0)
        min_knee = metrics_summary.get("min_knee_flex_angle", 180.0)
        max_elbow = metrics_summary.get("max_elbow_extension", 180.0)

        # Pull shot heuristic: trunk leaning back or upright, high elbow extension across horizontal plane
        if avg_trunk < 2.0 and max_elbow > 140.0:
            return "Pull Shot", 0.82

        # Cut shot heuristic: horizontal bat play on off-side, high elbow extension
        if avg_trunk >= 2.0 and avg_trunk < 10.0 and max_elbow > 135.0:
            return "Cut Shot", 0.76

        # Forward Drive / Defence heuristics: forward trunk tilt
        if avg_trunk >= 10.0:
            if min_knee < 125.0:
                # Cover Drive / Straight Drive
                return "Cover Drive", 0.88
            else:
                return "Forward Defence", 0.85

        if min_knee < 135.0:
            return "Straight Drive", 0.78

        return "Forward Defence", 0.70

    def _extract_feature_vector(
        self,
        frame_metrics: List[Dict[str, float]],
        summary: Dict[str, float]
    ) -> np.ndarray:
        """
        Extracts fixed-length 12-dimensional feature vector for ML classifiers.
        """
        trunks = [m.get("trunk_inclination", 0.0) for m in frame_metrics]
        l_knees = [m.get("left_knee_angle", 180.0) for m in frame_metrics]
        r_knees = [m.get("right_knee_angle", 180.0) for m in frame_metrics]
        l_elbows = [m.get("left_elbow_angle", 180.0) for m in frame_metrics]
        r_elbows = [m.get("right_elbow_angle", 180.0) for m in frame_metrics]

        return np.array([
            summary.get("head_instability_score", 0.0),
            summary.get("min_knee_flex_angle", 180.0),
            summary.get("avg_trunk_inclination", 0.0),
            summary.get("max_elbow_extension", 0.0),
            np.mean(trunks) if trunks else 0.0,
            np.std(trunks) if trunks else 0.0,
            np.min(l_knees) if l_knees else 180.0,
            np.min(r_knees) if r_knees else 180.0,
            np.max(l_elbows) if l_elbows else 0.0,
            np.max(r_elbows) if r_elbows else 0.0,
            np.mean(l_knees) if l_knees else 180.0,
            np.mean(r_knees) if r_knees else 180.0,
        ])
