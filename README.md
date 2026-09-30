# AI-Powered Virtual Cricket Coach for Automated Cricket Technique Analysis

Academic AI and computer-vision prototype for automated cricket batting technique analysis. The system accepts video uploads of a single cricket player performing a batting shot, extracts 3D human pose landmarks using MediaPipe and OpenCV, calculates exact biomechanical joint angles and movement stability features, classifies the shot type, evaluates technique deviations against coaching rules, and generates explainable feedback on an interactive sports dashboard.

---

## 1. Overview & Problem Statement

Cricket technique coaching traditionally relies on subjective visual observations by experienced coaches. Access to expert biomechanical analysis is often restricted to elite national academies due to the cost of specialized optical motion capture equipment. 

This project builds an accessible, academic computer-vision prototype that automates biomechanical analysis from standard single-camera video uploads, delivering evidence-backed coaching feedback and performance tracking.

---

## 2. Supported Batting Shots & Biomechanical Features

### Supported Shots (5 Categories):
1. **Forward Defence**
2. **Straight Drive**
3. **Cover Drive**
4. **Pull Shot**
5. **Cut Shot**

### Analyzed Biomechanical Features:
- **Joint Angles**: Front & Back Knee Angle, Elbow Angle, Hip Angle.
- **Posture & Alignment**: Trunk Inclination relative to vertical, Shoulder Line Orientation.
- **Movement Stability**: Head Instability Index (standard deviation of head displacement across shot trajectory).
- **Lower Body Stance**: Stance width ratio normalized by hip breadth.
- **Center of Mass (CoM)**: Mid-hip tracking throughout downswing and follow-through.

---

## 3. Technology Stack

- **Backend**: Python 3.14+, FastAPI, Uvicorn, SQLAlchemy ORM (SQLite / PostgreSQL ready).
- **Computer Vision & AI**: OpenCV, MediaPipe Pose Landmarker (33 3D joints), NumPy, SciPy, Scikit-learn (Random Forest).
- **Frontend Dashboard**: Tailwind CSS, Chart.js, FontAwesome, embedded responsive HTML5 web app + Next.js / React TypeScript components.
- **Testing & Tooling**: Pytest, Synthetic Video Generator.

---

## 4. Complete System Workflow

```
VIDEO UPLOAD → VIDEO VALIDATION → PREPROCESSING & FRAME EXTRACTION 
→ POSE LANDMARK EXTRACTION → LANDMARK TRACKING → BIOMECHANICAL FEATURE EXTRACTION 
→ SHOT CLASSIFICATION → TECHNIQUE ANALYSIS → FEEDBACK GENERATION 
→ RESULT VISUALIZATION → PERFORMANCE HISTORY
```

---

## 5. Quick Start & How to Run

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: (Optional) Generate Synthetic Cricket Video for Offline Testing

```bash
python scratch/generate_sample_video.py
```
*Generates `data/raw/sample_cover_drive.mp4`.*

### Step 3: Launch FastAPI Server & Web Dashboard

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### Step 4: Open Dashboard in Browser

Open your browser and navigate to:
`http://localhost:8000`

---

## 6. How to Upload a Video & Analyze

1. On the web dashboard at `http://localhost:8000`, click **Click or drop cricket video here**.
2. Select a valid `.mp4` or `.mov` clip (e.g., `data/raw/sample_cover_drive.mp4`).
3. (Optional) Choose an explicit shot hint or leave set to **Auto-Detect Shot Classification**.
4. Click **Start Technique Analysis**.
5. View the rendered **Pose Overlay Video**, calculated joint angles, radar charts, and explainable coaching observations.

---

## 7. API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web Application Dashboard UI |
| `GET` | `/api/health` | System health check & loaded models status |
| `POST` | `/api/videos/upload` | Upload & validate cricket video file |
| `POST` | `/api/analysis/start` | Trigger end-to-end video analysis pipeline |
| `GET` | `/api/analysis/{id}` | Retrieve analysis status & results |
| `GET` | `/api/athletes/{id}/history` | Retrieve athlete performance history |

---

## 8. Unit Tests Execution

Run the backend unit test suite:

```bash
pytest backend/tests
```

All 10 unit tests verify mathematical angle formulas, numerical clamping safety, shot classification thresholds, feedback generation, and API endpoints.

---

## 9. Academic Limitations & Privacy Considerations

- **Academic Scope**: Designed as a university technology prototype, not a medical or physical diagnostic tool.
- **Single-Camera Setup**: 3D joint depths from single-camera videos are subject to perspective distortion.
- **Privacy Notice**: Uploaded videos are stored with randomly generated UUID filenames and processed locally.
