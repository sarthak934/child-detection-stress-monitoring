from flask import Flask, render_template, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "child-detection-dashboard-firebase-adminsdk-fbsvc-9fe3ed0524.json"
)
firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/latest")
def latest():
    docs = (
        db.collection("detections")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(10)
        .stream()
    )

    results = []
    for doc in docs:
        results.append(doc.to_dict())

    response = make_response(jsonify(results))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)
