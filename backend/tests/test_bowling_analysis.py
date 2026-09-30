import pytest
from backend.app.analysis.bowling_biomechanics import BowlingBiomechanicsCalculator
from backend.app.analysis.bowling_analyzer import BowlingAnalyzer

def test_bowling_action_classification():
    # Synchronized alignment (0 degree divergence) -> Side-on Action
    action_name, is_mixed = BowlingBiomechanicsCalculator.classify_bowling_action(
        alignment_diff=5.0,
        shoulder_orientation=10.0
    )
    assert "Side-on" in action_name
    assert is_mixed is False

    # Large divergence (45 degree divergence) -> Mixed Action Risk
    action_name, is_mixed = BowlingBiomechanicsCalculator.classify_bowling_action(
        alignment_diff=45.0,
        shoulder_orientation=10.0
    )
    assert "Mixed Action" in action_name
    assert is_mixed is True

def test_bowling_summary_computation():
    frame_metrics = [
        {
            "front_knee_brace_angle": 165.0,
            "bowling_elbow_angle": 174.0,
            "shoulder_hip_alignment_diff": 12.0,
            "trunk_lateral_flexion": 22.0,
            "release_wrist_y": 0.25 # Highest wrist elevation
        }
    ]

    summary = BowlingBiomechanicsCalculator.compute_bowling_delivery_summary(frame_metrics)
    assert summary["front_knee_brace_angle_release"] == 165.0
    assert summary["icc_compliant"] is True
    assert summary["is_mixed_action_risk"] is False

    obs = BowlingAnalyzer.analyze_bowling_delivery(summary)
    assert len(obs) >= 3
    assert any("Action Legality" in o["category"] for o in obs)
    assert any("Kinetic Chain" in o["category"] for o in obs)
