# Child Detection & CLoud Deployment

A real-time computer vision system that detects people in video streams, identifies children using pose-based body proportion analysis, flags stress-like postures (hands on head), stores detection events historically using Firebase, and visualizes results via a Flask dashboard.

---

## Key Features

- Real-time multi-person detection using YOLOv8
- Lightweight person identity assignment across frames
- Pose estimation using MediaPipe Pose
- Explainable child vs adult classification based on body proportions
- Stress-like posture detection (hands on head) for children
- Historical event logging using Firebase Firestore
- Read-only Flask API for clean data access
- Web dashboard for monitoring and filtering detections

---

## System Architecture

Video Input → YOLOv8 → MediaPipe Pose → Feature Extraction
→ Firebase (Historical Storage) → Flask API → Web Dashboard


Each component is modular and designed with a single responsibility.

---

## Repository Structure

child-detection-stress-monitoring/
├── detection/ # Vision pipeline (YOLO + Pose + Firebase logging)
├── dashboard/ # Flask backend and HTML templates
├── sop/ # Detailed SOP documentation
│ └── SOP_Workflow.md
├── README.md
└── .gitignore


---

## Documentation

- **Detailed Workflow & Design:**  
  Refer to `sop/SOP_Workflow.md` for a complete step-by-step explanation of the detection pipeline, feature extraction, data flow, and system design decisions.

---

## How the System Works (High Level)

1. Video frames are processed in real time
2. YOLOv8 detects people in each frame
3. Each detected person is assigned a persistent ID
4. MediaPipe Pose extracts body landmarks
5. Child vs adult classification is performed using body proportions
6. Hands-on-head posture is detected for stress-like events
7. Detection events are logged to Firebase
8. Flask retrieves historical data
9. Dashboard visualizes and filters detections

---

## Notes

- Stress detection refers to **posture-based events**, not psychological or emotional diagnosis
- Firebase is used as an **append-only historical datastore**
- Flask contains **no machine learning or vision logic** by design

---

## Future Enhancements

- Temporal aggregation of stress posture events
- Multi-camera and multi-location support
- Alerting based on sustained posture patterns
- Advanced tracking integration if required
