"""Prediction and analytics service for the fitness dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd

from config import DATASET_PATH, FEATURE_LABELS, MODEL_DIR

# Container for all model-related assets loaded at startup and we can acess it by self.asset
@dataclass
class ModelAssets: 
    scaler: Any
    regressor: Any
    classifier: Any
    clusterer: Any
    label_encoder: Any
    cluster_map: dict[int, str] | dict[str, str]
    features: list[str]
    metadata: dict[str, Any]


def load_model_assets() -> ModelAssets:
    with open(MODEL_DIR / "metadata.json", encoding="utf-8") as handle:
        metadata = json.load(handle)

    regressor = joblib.load(MODEL_DIR / "regression.pkl")
    classifier = joblib.load(MODEL_DIR / "classifier.pkl")
    clusterer = joblib.load(MODEL_DIR / "clustering.pkl")

    for model in (regressor, classifier, clusterer):
        if hasattr(model, "n_jobs"):
            model.n_jobs = 1

    return ModelAssets(
        scaler=joblib.load(MODEL_DIR / "scaler.pkl"),
        regressor=regressor,
        classifier=classifier,
        clusterer=clusterer,
        label_encoder=joblib.load(MODEL_DIR / "label_encoder.pkl"),
        cluster_map=joblib.load(MODEL_DIR / "cluster_map.pkl"),
        features=joblib.load(MODEL_DIR / "features.pkl"),
        metadata=metadata,
    )


class PredictionService:
    def __init__(self, assets: ModelAssets):
        self.assets = assets
        self.score_min, self.score_max = self._load_score_bounds()
        self.score_span = max(self.score_max - self.score_min, 1.0)

    def _load_score_bounds(self) -> tuple[float, float]:
        try:
            df = pd.read_csv(DATASET_PATH)
            df.columns = df.columns.str.strip()
            scores = df.apply(lambda row: self.compute_engineered_score(row.to_dict()), axis=1)
            return float(scores.min()), float(scores.max())
        except Exception:
            return 30.0, 75.0

    def compute_engineered_score(self, data: dict[str, Any]) -> float:
        score = 0.0
        score += min(float(data.get("Calories_Burned", 0)) / 2000 * 25, 25)
        score += min(float(data.get("Session_Duration (hours)", 0)) / 2.0 * 15, 15)
        score += max(0, (50 - float(data.get("Fat_Percentage", 50))) / 50 * 20)
        score += min(float(data.get("Workout_Frequency (days/week)", 0)) / 7 * 15, 15)
        score += min((float(data.get("Experience_Level", 1)) - 1) / 2 * 10, 10)
        score += max(0, (100 - float(data.get("Resting_BPM", 100))) / 100 * 10)
        score += min(float(data.get("Water_Intake (liters)", 0)) / 4.0 * 5, 5)
        return round(min(max(score, 0), 100), 2)

    def practical_score(self, raw_score: float) -> float:
        normalized = (raw_score - self.score_min) / self.score_span * 100
        return round(min(max(normalized, 0), 100), 1)

    @staticmethod
    def score_band(score: float) -> str:
        if score >= 80:
            return "Elite"
        if score >= 60:
            return "Strong"
        if score >= 40:
            return "Building"
        return "Starting"

    def reliability_summary(self) -> dict[str, Any]:
        regression_r2 = float(self.assets.metadata["regression"]["rf_r2"])
        classification_acc = float(self.assets.metadata["classification"]["accuracy"])
        combined = (regression_r2 + classification_acc) / 2
        if combined >= 0.93:
            label = "High"
        elif combined >= 0.85:
            label = "Moderate"
        else:
            label = "Experimental"
        return {
            "label": label,
            "score": round(combined * 100, 1),
            "summary": "Based on holdout regression fit and classifier accuracy, not a personal certainty score.",
            "regression_r2": regression_r2,
            "classification_acc": classification_acc,
        }

    def build_validation_messages(self, data: dict[str, Any]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        def add(msg_type: str, icon: str, text: str):
            messages.append({"type": msg_type, "icon": icon, "text": text})

        max_bpm = float(data.get("Max_BPM", 0))
        avg_bpm = float(data.get("Avg_BPM", 0))
        resting_bpm = float(data.get("Resting_BPM", 0))
        duration = float(data.get("Session_Duration (hours)", 0))
        calories = float(data.get("Calories_Burned", 0))
        freq = float(data.get("Workout_Frequency (days/week)", 0))
        water = float(data.get("Water_Intake (liters)", 0))
        fat_pct = float(data.get("Fat_Percentage", 0))
        bmi = float(data.get("BMI", 0))
        experience = float(data.get("Experience_Level", 1))

        if avg_bpm > max_bpm:
            add("danger", "!", "Average BPM is higher than max BPM. Adjust those values before trusting this prediction.")
        if resting_bpm >= avg_bpm:
            add("warning", "HR", "Resting BPM should usually stay below average workout BPM. This looks internally inconsistent.")
        if duration >= 2.0 and calories < 300:
            add("warning", "Cal", "A long workout with very low calorie burn is unlikely. Check duration or calorie estimate.")
        if calories > max(duration, 0.25) * 1200:
            add("warning", "Cal", "Calorie burn looks aggressive for the selected duration. Treat the score as exploratory.")
        if water < 2.0 and duration > 1.5:
            add("info", "H2O", "Hydration is light for this training volume. Recovery quality may be overstated.")
        if freq >= 6 and duration >= 2.0:
            add("info", "Load", "Training load is very high. Add recovery days so the plan stays realistic.")
        if experience >= 3 and freq <= 2:
            add("info", "Lvl", "Advanced experience with low weekly frequency is possible, but it usually undercuts the label.")
        # if bmi < 18.5 and fat_pct > 30:
        #     add("warning", "BMI", "Low BMI with high body-fat is unusual. Recheck weight, height, or body-fat input.")

        if not messages:
            add("success", "OK", "Inputs look internally consistent enough for a useful estimate.")

        return messages[:4]

    @staticmethod
    def build_metric_feedback(data: dict[str, Any]) -> list[dict[str, str]]:
        feedback: list[dict[str, str]] = []
        resting_bpm = float(data.get("Resting_BPM", 0))
        water = float(data.get("Water_Intake (liters)", 0))
        freq = float(data.get("Workout_Frequency (days/week)", 0))
        bmi = float(data.get("BMI", 0))

        if resting_bpm <= 60:
            feedback.append({"label": "Resting BPM", "value": "Strong cardio base"})
        elif resting_bpm <= 75:
            feedback.append({"label": "Resting BPM", "value": "Healthy range"})
        else:
            feedback.append({"label": "Resting BPM", "value": "Cardio fitness can improve"})

        if water >= 3:
            feedback.append({"label": "Hydration", "value": "Recovery friendly"})
        elif water >= 2:
            feedback.append({"label": "Hydration", "value": "Adequate"})
        else:
            feedback.append({"label": "Hydration", "value": "Below ideal"})

        if freq >= 5:
            feedback.append({"label": "Frequency", "value": "Consistent routine"})
        elif freq >= 3:
            feedback.append({"label": "Frequency", "value": "Moderate routine"})
        else:
            feedback.append({"label": "Frequency", "value": "Low training frequency"})

        if bmi < 18.5:
            feedback.append({"label": "BMI", "value": "Below target range"})
        elif bmi <= 24.9:
            feedback.append({"label": "BMI", "value": "Healthy range"})
        elif bmi <= 29.9:
            feedback.append({"label": "BMI", "value": "Above target range"})
        else:
            feedback.append({"label": "BMI", "value": "High health risk"})

        return feedback

    def build_goal_planner(self, data: dict[str, Any], raw_score: float, target_practical: float | None) -> dict[str, Any]:
        current_practical = self.practical_score(raw_score)
        gender = str(data.get("Gender", "male")).lower()
        current = {
            "Calories_Burned": float(data.get("Calories_Burned", 0)),
            "Session_Duration (hours)": float(data.get("Session_Duration (hours)", 0)),
            "Workout_Frequency (days/week)": float(data.get("Workout_Frequency (days/week)", 0)),
            "Resting_BPM": float(data.get("Resting_BPM", 0)),
            "Water_Intake (liters)": float(data.get("Water_Intake (liters)", 0)),
            "Fat_Percentage": float(data.get("Fat_Percentage", 0)),
        }

        def scenario(field: str, target: float, title: str, action: str, eta: str, difficulty: str):
            updated = dict(data)
            updated[field] = target
            raw_gain = max(self.compute_engineered_score(updated) - self.compute_engineered_score(data), 0)
            if raw_gain <= 0:
                return None
            practical_gain = round(raw_gain / self.score_span * 100, 1)
            return {
                "field": field,
                "title": title,
                "action": action,
                "current": round(current[field], 2),
                "target": round(target, 2),
                "eta": eta,
                "difficulty": difficulty,
                "estimated_gain": practical_gain,
                "estimated_raw_gain": round(raw_gain, 2),
            }

        fat_target_floor = 18 if gender == "male" else 25
        candidates = [
            scenario("Calories_Burned", min(max(current["Calories_Burned"] + 200, 800), 1200), "Increase session output", "Push calorie burn toward 800-1200 kcal with tighter pace or longer cardio blocks.", "2-4 weeks", "Medium"),
            scenario("Session_Duration (hours)", min(max(current["Session_Duration (hours)"] + 0.25, 1.0), 1.5), "Extend sessions slightly", "Add 15-30 minutes to your average session to raise training volume without a major routine change.", "1-2 weeks", "Easy"),
            scenario("Workout_Frequency (days/week)", min(max(current["Workout_Frequency (days/week)"] + 1, 4), 5), "Train one more day", "Move from your current weekly frequency toward 4-5 sessions with one recovery-focused day.", "1-3 weeks", "Medium"),
            scenario("Resting_BPM", max(current["Resting_BPM"] - 5, 58), "Improve cardio efficiency", "A lower resting BPM usually follows steady zone-2 work, sleep, and recovery consistency.", "4-8 weeks", "Hard"),
            scenario("Water_Intake (liters)", min(max(current["Water_Intake (liters)"] + 0.8, 2.8), 3.5), "Tighten hydration", "Lift daily water intake toward 2.8-3.5 L so performance and recovery are less constrained.", "1 week", "Easy"),
            scenario("Fat_Percentage", max(fat_target_floor, current["Fat_Percentage"] - 4), "Improve body composition", "Reduce body-fat gradually through calorie control and resistance training while keeping protein high.", "6-12 weeks", "Hard"),
        ]

        ranked = [item for item in candidates if item is not None]
        ranked.sort(key=lambda item: item["estimated_gain"], reverse=True)

        target = float(target_practical) if target_practical is not None else min(current_practical + 12, 100)
        target_gap = max(round(target - current_practical, 1), 0)
        cumulative = 0.0
        recommended = []
        for item in ranked:
            recommended.append(item)
            cumulative += item["estimated_gain"]
            if cumulative >= target_gap and target_gap > 0:
                break

        return {
            "target_practical_score": round(target, 1),
            "current_practical_score": current_practical,
            "gap_to_target": target_gap,
            "can_close_gap": cumulative >= target_gap if target_gap > 0 else True,
            "recommended_actions": recommended[:3],
            "chart": [{"label": item["title"], "gain": item["estimated_gain"]} for item in ranked[:5]],
        }

    def generate_suggestions(self, data: dict[str, Any], fitness_score: float, fitness_level: str, lifestyle: str) -> list[dict[str, str]]:
        suggestions = []
        fi = self.assets.metadata["feature_importance"]

        calories = data.get("Calories_Burned", 500)
        fat_pct = data.get("Fat_Percentage", 25)
        freq = data.get("Workout_Frequency (days/week)", 3)
        duration = data.get("Session_Duration (hours)", 1.0)
        resting_bpm = data.get("Resting_BPM", 70)
        experience = data.get("Experience_Level", 1)
        bmi = data.get("BMI", 22)
        water = data.get("Water_Intake (liters)", 2.0)

        cal_impact = round(fi.get("Calories_Burned", 0.15) * 100, 1)
        if calories < 500:
            suggestions.append({"icon": "🔥", "type": "warning", "text": f"Low calorie burn is suppressing your fitness score by ~{cal_impact}%. Target 600-1000 kcal/session with higher-intensity workouts."})
        elif calories > 1200:
            suggestions.append({"icon": "⚡", "type": "success", "text": f"Excellent calorie burn. Your high output ({int(calories)} kcal) is boosting your score by ~{cal_impact}%."})

        fat_impact = round(fi.get("Fat_Percentage", 0.12) * 100, 1)
        if fat_pct > 30:
            suggestions.append({"icon": "📉", "type": "danger", "text": f"High body fat ({fat_pct}%) is reducing your fitness score by ~{fat_impact}%. Combine strength training with cardio to improve body composition."})
        elif fat_pct < 15:
            suggestions.append({"icon": "💪", "type": "success", "text": f"Excellent body composition ({fat_pct}% fat). This is adding ~{fat_impact}% to your fitness score."})

        freq_impact = round(fi.get("Workout_Frequency (days/week)", 0.10) * 100, 1)
        if freq < 3:
            suggestions.append({"icon": "📅", "type": "warning", "text": f"Exercising only {int(freq)} day(s)/week limits your progress by ~{freq_impact}%. Aim for 4-5 sessions per week for optimal gains."})
        elif freq >= 5:
            suggestions.append({"icon": "🏆", "type": "success", "text": f"High workout frequency ({int(freq)} days/week) is a key driver of your fitness score (+{freq_impact}%)."})

        dur_impact = round(fi.get("Session_Duration (hours)", 0.08) * 100, 1)
        if duration < 0.75:
            suggestions.append({"icon": "⏱", "type": "info", "text": f"Short sessions ({duration:.2f}h) are costing ~{dur_impact}% in score. Extending to 1-1.5 hours can significantly improve outcomes."})

        resting_impact = round(fi.get("Resting_BPM", 0.07) * 100, 1)
        if resting_bpm > 80:
            suggestions.append({"icon": "❤️", "type": "danger", "text": f"Elevated resting BPM ({int(resting_bpm)}) indicates low cardiovascular fitness, reducing score by ~{resting_impact}%. Add 20-min daily cardio."})
        elif resting_bpm < 60:
            suggestions.append({"icon": "🫀", "type": "success", "text": f"Athlete-level resting BPM ({int(resting_bpm)}) is contributing +{resting_impact}% to your score."})

        if water < 2.0:
            suggestions.append({"icon": "💧", "type": "warning", "text": f"Insufficient hydration ({water:.1f}L/day) is limiting recovery and performance. Drink at least 2.5-3.5L daily, especially on workout days."})

        if bmi > 30:
            suggestions.append({"icon": "⚖", "type": "danger", "text": f"BMI of {bmi:.1f} indicates obesity. Reducing body weight through calorie control and consistent cardio will substantially improve your fitness score."})
        elif 18.5 <= bmi <= 24.9:
            suggestions.append({"icon": "✅", "type": "success", "text": f"Healthy BMI ({bmi:.1f}) is supporting your overall fitness. Maintain with balanced nutrition."})

        if experience == 1 and fitness_score > 55:
            suggestions.append({"icon": "🚀", "type": "info", "text": "As a beginner with good metrics, consider progressing to intermediate programs to unlock the next level of gains."})

        if lifestyle == "Sedentary":
            suggestions.append({"icon": "🛋", "type": "danger", "text": "Sedentary lifestyle detected. Introduce daily movement; even 30-minute walks can shift your cluster toward Balanced within 4 weeks."})
        elif lifestyle == "Balanced":
            suggestions.append({"icon": "⚖", "type": "info", "text": "Balanced lifestyle. To reach the Active tier, increase either workout frequency or intensity."})

        if fitness_score < 45:
            suggestions.append({"icon": "🎯", "type": "danger", "text": f"Your current fitness score ({fitness_score:.1f}/100) places you in the lower quartile. Focus on the top 2 suggestions for the fastest improvement."})
        elif fitness_score >= 65:
            suggestions.append({"icon": "🌟", "type": "success", "text": f"Great fitness score ({fitness_score:.1f}/100). You are in the top tier. Maintain consistency and focus on recovery to sustain it."})

        return suggestions[:5]

    def predict(self, data: dict[str, Any]) -> dict[str, Any]:
        target_practical = data.get("Target_Practical_Score")
        feature_vector = pd.DataFrame([[float(data.get(feature, 0)) for feature in self.assets.features]], columns=self.assets.features)
        x_scaled = self.assets.scaler.transform(feature_vector)

        fitness_score = float(self.assets.regressor.predict(x_scaled)[0])
        fitness_score = round(min(max(fitness_score, 0), 100), 2)

        clf_pred = self.assets.classifier.predict(x_scaled)[0]
        fitness_level = self.assets.label_encoder.inverse_transform([clf_pred])[0]

        cluster_id = int(self.assets.clusterer.predict(x_scaled)[0])
        lifestyle = self.assets.cluster_map.get(cluster_id, self.assets.cluster_map.get(str(cluster_id), "Balanced"))

        current_practical_score = self.practical_score(fitness_score)
        reliability = self.reliability_summary()
        validation_messages = self.build_validation_messages(data)
        metric_feedback = self.build_metric_feedback(data)
        goal_planner = self.build_goal_planner(data, fitness_score, target_practical)
        suggestions = self.generate_suggestions(data, fitness_score, fitness_level, lifestyle)

        return {
            "fitness_score": fitness_score,
            "practical_score": current_practical_score,
            "score_context": {
                "observed_min": round(self.score_min, 2),
                "observed_max": round(self.score_max, 2),
                "band": self.score_band(current_practical_score),
                "summary": "Practical score is normalized to the observed training-data range, so 100 means top-of-dataset rather than a theoretical perfect human.",
            },
            "fitness_level": fitness_level,
            "lifestyle": lifestyle,
            "suggestions": suggestions,
            "validation_messages": validation_messages,
            "metric_feedback": metric_feedback,
            "goal_planner": goal_planner,
            "opportunity_chart": goal_planner["chart"],
            "reliability": reliability,
            "model_confidence": {
                "regression_r2": reliability["regression_r2"],
                "classification_acc": reliability["classification_acc"],
            },
        }

    def analytics_payload(self) -> dict[str, Any]:
        metadata = self.assets.metadata
        return {
            "model_comparison": {
                "models": ["Linear Regression", "RandomForest"],
                "r2": [metadata["regression"]["lr_r2"], metadata["regression"]["rf_r2"]],
                "rmse": [metadata["regression"]["lr_rmse"], metadata["regression"]["rf_rmse"]],
            },
            "feature_importance": metadata["feature_importance"],
            "distributions": metadata["distributions"],
            "correlation": metadata.get("correlation", {}),
            "corr_features": metadata.get("corr_features", []),
            "dataset_stats": metadata["dataset_stats"],
            "clustering": metadata["clustering"],
            "classification": metadata["classification"],
        }

    @property
    def metadata(self) -> dict[str, Any]:
        return self.assets.metadata

    @property
    def feature_labels(self) -> dict[str, str]:
        return FEATURE_LABELS
