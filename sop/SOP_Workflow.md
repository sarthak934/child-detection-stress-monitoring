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

The system follows a modular, event-driven pipeline:

Video Input → YOLOv8 → MediaPipe Pose → Feature Extraction
→ Firebase (Historical Storage) → Flask API → Web Dashboard




Each component has a clearly defined responsibility, enabling scalability and maintainability.

---

## 3. Person Detection using YOLOv8

- YOLOv8 performs single-shot object detection on each video frame
- Outputs bounding boxes, class labels, and confidence scores
- Only detections labeled as **person** are processed further
- Enables real-time multi-person detection with low latency

YOLOv8 is chosen for its balance of speed, accuracy, and real-time performance.

---

## 4. Person Identity Assignment

- Each detected person is assigned a temporary persistent ID
- Identity continuity is maintained using spatial proximity across frames
- Avoids heavy multi-object tracking frameworks while preserving ID consistency
- Enables event-level tracking across consecutive frames

---

## 5. Pose Estimation using MediaPipe

- MediaPipe Pose extracts 33 body landmarks per detected person
- Landmarks are normalized and resolution-independent
- Enables posture and body-proportion analysis even when faces are not visible
- Lightweight and suitable for real-time inference

---

## 6. Child vs Adult Classification

- Classification is based on relative body proportions
- Torso and leg lengths are estimated using pose landmarks
- A leg-to-torso ratio is computed
- Lower ratios indicate child-like body proportions

**Outputs**
- `is_child` (Boolean)
- `child_score` (confidence score)

This approach is explainable and avoids opaque age-prediction models.

---

## 7. Stress Posture Detection (Hands on Head)

- Wrist and head landmarks are analyzed using pose data
- If both wrists are spatially close to the head, posture is flagged
- A stress flag is generated **only when**:
  - The detected person is classified as a child
  - Hands-on-head posture is detected

**Note**
- This represents stress-like posture events
- It does not claim psychological or emotional stress detection

---

## 8. Event Construction and Logging

Each detection event is constructed as a single immutable record containing:
- Timestamp (UTC)
- Person ID
- Child classification and confidence score
- Upper and lower clothing color
- Hands-on-head posture flag
- Stress event flag

Each event represents a snapshot of system inference at a specific time.

---

## 9. Firebase as Historical Datastore

- Firebase Firestore is used for append-only historical storage
- Cloud-hosted and automatically scalable
- Schema-flexible, allowing new features without database migrations
- Supports concurrent access from multiple systems
- Acts as the single source of truth for detection events

Firebase enables long-term storage and distributed access to detection data.

---

## 10. Flask Backend (Data Access Layer)

- Flask serves as a read-only API layer
- Fetches and normalizes detection data from Firebase
- No vision or machine learning logic exists in the backend
- Prevents logic duplication and ensures clean separation of concerns

---

## 11. Web Dashboard

- The dashboard consumes data exposed by Flask APIs
- Displays recent detections, child confidence scores, and stress flags
- Enables filtering based on:
  - Child vs adult classification
  - Stress posture events
  - Temporal ordering
  - Person identity
- Supports both real-time monitoring and historical review

---

## 12. Multi-System Accessibility

- Firebase enables access from multiple machines and locations
- Detection pipelines and dashboards can operate independently
- Supports distributed deployments and remote monitoring
- Eliminates reliance on local storage or single-system execution

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
