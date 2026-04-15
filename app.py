"""Fitness Habit Analyzer Flask application."""

from flask import Flask, jsonify, render_template, request

from services.prediction_service import PredictionService, load_model_assets
from validators import ValidationError, validate_prediction_payload

app = Flask(__name__)
prediction_service = PredictionService(load_model_assets())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/progress")
def progress():
    return render_template("progress.html")


@app.route("/health")
def health():
    return render_template("health.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = validate_prediction_payload(request.get_json(force=True))
        return jsonify(prediction_service.predict(payload))
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/metadata")
def get_metadata():
    return jsonify(prediction_service.metadata)


@app.route("/api/analytics")
def get_analytics():
    return jsonify(prediction_service.analytics_payload())


if __name__ == "__main__":
    print("Fitness Habit Analyzer starting on http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
