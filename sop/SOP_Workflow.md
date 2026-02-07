# Standard Operating Procedure (SOP)
## Child Detection & Stress Posture Monitoring System

---

## 1. Objective

- Build a real-time computer vision system to detect people in video streams
- Identify children using pose-based body proportion analysis
- Detect stress-like posture events (hands on head)
- Store all detection events historically using Firebase
- Visualize detections through a Flask-based dashboard

---

## 2. System Architecture Overview

![System Architecture](images/system_architecture.png)

Video Input → YOLOv8 → MediaPipe Pose → Feature Extraction
→ Firebase (Historical Storage) → Flask API → Web Dashboard



---

## 3. Person Detection using YOLOv8

![YOLO Detection](images/yolo_detection.png)

- YOLOv8 performs single-shot object detection on each video frame
- Outputs bounding boxes, class labels, and confidence scores
- Only detections labeled as **person** are processed further
- Enables real-time multi-person detection with low latency

---

## 4. Person Identity Assignment

![Person Tracking](images/person_tracking.png)

- Each detected person is assigned a temporary persistent ID
- ID continuity is maintained using spatial proximity across frames
- Enables event-level tracking without heavy tracking frameworks
- Supports consistent identification across multiple frames

---

## 5. Pose Estimation using MediaPipe

![MediaPipe Pose Landmarks](images/pose_landmarks.png)

- MediaPipe Pose extracts 33 body landmarks per detected person
- Landmarks are normalized and resolution-independent
- Enables posture and body-proportion analysis even when faces are not visible

---

## 6. Child vs Adult Classification

![Body Proportion Analysis](images/body_proportion.png)

- Classification is based on relative body proportions
- Torso and leg lengths are estimated using pose landmarks
- A leg-to-torso ratio is computed
- Lower ratios indicate child-like body proportions

**Outputs**
- `is_child` (Boolean)
- `child_score` (confidence score)

This approach is explainable and avoids opaque age prediction models.

---

## 7. Stress Posture Detection (Hands on Head)

![Hands on Head Detection](images/hands_on_head.png)

- Wrist and head landmarks are analyzed
- If both wrists are close to the head, posture is flagged
- Stress flag is generated **only if**:
  - The person is classified as a child
  - Hands-on-head posture is detected

**Important**
- This represents stress-like posture events
- It does NOT claim psychological or emotional stress

---

## 8. Event Construction and Logging

Each detection event is constructed as a single immutable record containing:
- Timestamp (UTC)
- Person ID
- Child classification and confidence score
- Upper and lower clothing color
- Hands-on-head posture flag
- Stress event flag

Events represent historical snapshots of detections.

---

## 9. Firebase as Historical Datastore

![Firebase Console](images/firebase_console.png)

- Firebase Firestore is used for append-only historical storage
- Cloud-hosted and automatically scalable
- Schema-flexible, allowing feature expansion without migrations
- Supports concurrent access from multiple systems
- Acts as the single source of truth for detection events

---

## 10. Flask Backend (Data Access Layer)

![Flask API Flow](images/flask_api_flow.png)

- Flask serves as a read-only API layer
- Fetches and normalizes detection data from Firebase
- No vision or ML logic exists in Flask
- Prevents logic duplication and ensures clean separation of concerns

---

## 11. Web Dashboard

![Dashboard View](images/dashboard_view.png)

- Dashboard fetches data from Flask APIs
- Displays:
  - Person ID
  - Child classification confidence
  - Appearance attributes
  - Stress posture flags
- Supports filtering based on:
  - Child vs adult
  - Stress events
  - Temporal ordering
  - Person identity

---

## 12. Multi-System Accessibility

- Firebase enables access from multiple machines and locations
- Detection pipelines and dashboards can run independently
- Supports distributed deployments and remote monitoring
- No dependency on local storage or single-machine execution

---

## 13. End-to-End Workflow Summary

1. Video frame captured
2. Person detected using YOLOv8
3. Person ID assigned
4. Pose landmarks extracted
5. Child classification performed
6. Stress posture detected
7. Event logged to Firebase
8. Data fetched by Flask
9. Dashboard visualizes results

---

## 14. Design Philosophy

- Detection logic → Vision pipeline
- Storage → Firebase
- Aggregation → Flask
- Visualization → Dashboard

Each layer has a single responsibility, ensuring scalability, explainability, and maintainability.
