import cv2, warnings
warnings.filterwarnings("ignore")

import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from datetime import datetime

# ---------------- FIREBASE ----------------
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "child-detection-dashboard-firebase-adminsdk-fbsvc-9fe3ed0524.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- CONFIG ----------------
VIDEO_PATH = "video_sample.mp4"
CONF_THRES = 0.3
WRITE_INTERVAL = 30   # frames

# ---------------- MODELS ----------------
model = YOLO("yolov8n.pt")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ---------------- TRACKING ----------------
next_person_id = 1
tracks = {}
DIST_THRESH = 60

def assign_person_id(cx, cy):
    global next_person_id
    for pid, (px, py, _) in tracks.items():
        if abs(cx - px) < DIST_THRESH and abs(cy - py) < DIST_THRESH:
            tracks[pid] = (cx, cy, 0)
            return pid
    pid = next_person_id
    next_person_id += 1
    tracks[pid] = (cx, cy, 0)
    return pid

# ---------------- UTILITIES ----------------
def dominant_color(img):
    if img is None or img.size == 0:
        return "unknown"

    img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = np.median(hsv.reshape(-1, 3), axis=0)

    if v < 50: return "black"
    if s < 40 and v > 200: return "white"
    if h < 10 or h > 170: return "red"
    if h < 35: return "yellow"
    if h < 85: return "green"
    if h < 135: return "blue"
    return "other"

# ---------------- HANDS ON HEAD ----------------
def hands_on_head(res):
    if not res or not res.pose_landmarks:
        return False

    lm = res.pose_landmarks.landmark
    nose = lm[0]
    lw = lm[15]
    rw = lm[16]

    def close(a, b, th=0.12):
        return abs(a.x - b.x) < th and abs(a.y - b.y) < th

    return close(lw, nose) and close(rw, nose)

# ---------------- CHILD CLASSIFIER ----------------
def child_classifier(crop, bbox_h):
    if crop is None or crop.size == 0:
        return False, 0.0, None

    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)

    if not res.pose_landmarks:
        rel = bbox_h / 720
        return rel < 0.35, round(1 - rel, 2), res

    lm = res.pose_landmarks.landmark

    try:
        shoulder_y = (lm[11].y + lm[12].y) / 2
        hip_y = (lm[23].y + lm[24].y) / 2
        knee_y = (lm[25].y + lm[26].y) / 2

        torso = abs(hip_y - shoulder_y)
        leg = abs(knee_y - hip_y)

        ratio = leg / (torso + 1e-6)

        is_child = ratio < 1.1
        score = round(1.3 - ratio, 2)

        return is_child, max(0.0, min(score, 1.0)), res

    except:
        return False, 0.0, res

# ---------------- VIDEO ----------------
cap = cv2.VideoCapture(VIDEO_PATH)
frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    results = model(frame, conf=CONF_THRES, verbose=False)[0]

    for b in results.boxes:
        if results.names[int(b.cls[0])] != "person":
            continue

        x1, y1, x2, y2 = map(int, b.xyxy[0])
        if y2 <= y1 or x2 <= x1:
            continue

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        person_id = assign_person_id(cx, cy)

        crop = frame[y1:y2, x1:x2]
        upper = dominant_color(crop[:crop.shape[0] // 2])
        lower = dominant_color(crop[crop.shape[0] // 2:])

        is_child, child_score, pose_res = child_classifier(crop, y2 - y1)
        hands_head = hands_on_head(pose_res)
        stress_flag = bool(is_child and hands_head)

        # -------- FINAL RESULT OBJECT --------
        result = {
            "timestamp": datetime.utcnow(),
            "person_id": person_id,
            "is_child": is_child,
            "child_score": child_score,
            "upper_color": upper,
            "lower_color": lower,
            "hands_on_head": hands_head,
            "stress_flag": stress_flag
        }

        # -------- CMD OUTPUT --------
        if frame_idx % WRITE_INTERVAL == 0:
            print(
                f"[{result['timestamp']}] "
                f"ID={person_id} | "
                f"{'CHILD' if is_child else 'ADULT'} | "
                f"Score={child_score} | "
                f"HandsOnHead={hands_head} | "
                f"STRESSED={stress_flag} | "
                f"Upper={upper} | Lower={lower}"
            )

            # -------- FIREBASE WRITE --------
            db.collection("detections").add(result)

        # -------- DRAW --------
        color = (0, 0, 255) if stress_flag else (0, 255, 0)
        label = f"ID {person_id} | {'Child' if is_child else 'Adult'} | {child_score}"
        if stress_flag:
            label += " | STRESSED"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame, label, (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )

    cv2.imshow("Child Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

