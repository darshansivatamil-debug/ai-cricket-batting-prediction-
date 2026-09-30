# Project Architecture & Future Expansion Roadmap

## 1. System Components Architecture

```
                               ┌───────────────────────────┐
                               │     Client Browser /      │
                               │   Dashboard UI (HTML/React)│
                               └─────────────┬─────────────┘
                                             │ REST API HTTP
                               ▼             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Web Backend                            │
│  ┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────┐  │
│  │     Videos Router     │ │  Analysis Router  │ │  Athletes Router  │  │
│  └───────────┬───────────┘ └─────────┬─────────┘ └─────────┬─────────┘  │
└──────────────┼───────────────────────┼─────────────────────┼────────────┘
               │                       │                     │
               ▼                       ▼                     ▼
┌───────────────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│     Vision Pipeline       │ │  Biomechanics   │ │   SQLAlchemy ORM     │
│ (OpenCV + MediaPipe 3D)   │ │ & Feedback Engine│ │  (SQLite/PostgreSQL) │
└───────────────────────────┘ └─────────────────┘ └──────────────────────┘
```

---

## 2. Future-Ready Architecture (Scope Expansion Roadmap)

The system is designed with abstract interfaces to support seamless future extensions:
1. **3D Markerless Pose Estimation**: Replace 2D/3D landmarker with multi-camera triangulated 3D body mesh.
2. **Bat & Ball Tracking**: Integrate YOLOv8 object detection model for real-time bat angle & ball impact trajectory mapping.
3. **Temporal Deep Learning**: Plug PyTorch/TensorFlow Transformer models into `backend/app/ml/shot_classifier.py` without modifying API signatures.
4. **Edge AI / Mobile**: Export lightweight ONNX models for mobile execution (iOS CoreML / Android TFLite).
