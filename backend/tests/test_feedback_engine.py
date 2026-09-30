from backend.app.analysis.technique_analyzer import TechniqueAnalyzer
from backend.app.analysis.feedback_engine import FeedbackEngine

def test_technique_analysis_and_feedback():
    metrics_summary = {
        "head_instability_score": 6.5, # high instability
        "min_knee_flex_angle": 165.0, # stiff front knee
        "avg_trunk_inclination": 15.0,
        "max_elbow_extension": 110.0
    }
    
    obs = TechniqueAnalyzer.analyze_technique("Cover Drive", metrics_summary, [])
    assert len(obs) >= 2
    
    feedbacks = FeedbackEngine.generate_feedback(obs, "Cover Drive")
    assert len(feedbacks) == len(obs)
    assert any("Head" in f["category"] for f in feedbacks)
    assert any("Lower Body" in f["category"] for f in feedbacks)
