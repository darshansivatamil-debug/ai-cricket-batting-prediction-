from backend.app.ml.shot_classifier import ShotClassifier, SUPPORTED_SHOTS

def test_supported_shots_list():
    assert "Forward Defence" in SUPPORTED_SHOTS
    assert "Cover Drive" in SUPPORTED_SHOTS
    assert "Pull Shot" in SUPPORTED_SHOTS

def test_user_hint_override():
    classifier = ShotClassifier()
    shot, conf = classifier.classify_shot([], {}, user_hint="Straight Drive")
    assert shot == "Straight Drive"
    assert conf > 0.90

def test_empty_metrics_uncertain_classification():
    classifier = ShotClassifier()
    shot, conf = classifier.classify_shot([], {})
    assert shot == "Shot classification uncertain"
    assert conf == 0.0
