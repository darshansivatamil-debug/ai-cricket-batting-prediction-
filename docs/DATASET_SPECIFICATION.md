# Dataset Specification: AI Virtual Cricket Coach

This document defines the schema, recording guidelines, landmark structure, and train/val/test split protocols for building an empirical cricket shot classification and biomechanical technique dataset.

## 1. Data Schema

| Field Name | Type | Description | Example / Range |
| :--- | :--- | :--- | :--- |
| `athlete_id` | String | Anonymized unique player identifier | `ATH_001` |
| `video_id` | String | Unique video recording identifier | `VID_2026_09` |
| `shot_type` | Categorical | Ground truth shot label | `Forward Defence`, `Straight Drive`, `Cover Drive`, `Pull Shot`, `Cut Shot` |
| `camera_angle` | Categorical | Position of camera relative to batter | `Side-on`, `Front-on`, `45-degree Offside` |
| `fps` | Float | Video frame rate | `30.0` or `60.0` |
| `pose_landmarks` | Array[JSON] | 33 3D normalized MediaPipe landmark coordinates per frame | `[{x, y, z, visibility}, ...]` |
| `joint_angles` | JSON | Time-series joint angles | `{knee_angle: 124.5, elbow_angle: 110.2}` |
| `technique_annotations` | Array[String] | Expert coach annotations | `["Excessive head dip", "Good elbow elevation"]` |

---

## 2. Recording & Camera Guidelines

- **Player Visibility**: Full body must be visible from head to toe throughout the entire shot phase.
- **Lighting**: Adequate outdoor daylight or well-lit indoor nets. Avoid strong backlighting behind the batsman.
- **Camera Setup**: Mount camera on a tripod at waist height (approx. 1.1m) facing side-on or 45-degree offside to capture front knee stride and bat trajectory.

---

## 3. Data Splitting & Leakage Prevention

To evaluate model generalization to unseen players, datasets **must be split strictly by Athlete ID**:
- **Training Set (70%)**: Recordings from Athletes `ATH_001` through `ATH_070`.
- **Validation Set (15%)**: Recordings from Athletes `ATH_071` through `ATH_085`.
- **Test Set (15%)**: Recordings from Athletes `ATH_086` through `ATH_100`.

> [!CAUTION]
> **Data Leakage Prohibition**: Never assign different video clips of the *same athlete* across both training and test sets. Splitting by athlete ensures evaluation measures true generalization rather than athlete identity memorization.
