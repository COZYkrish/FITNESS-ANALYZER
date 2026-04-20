"""Application configuration and shared constants."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
DATASET_PATH = BASE_DIR / "gym_members_exercise_tracking_synthetic_data.csv"

FEATURE_LABELS = {
    "Age": "Age",
    "Weight (kg)": "Weight",
    "Height (m)": "Height",
    "Max_BPM": "Max Heart Rate",
    "Avg_BPM": "Avg Heart Rate",
    "Resting_BPM": "Resting BPM",
    "Session_Duration (hours)": "Session Duration",
    "Calories_Burned": "Calories Burned",
    "Fat_Percentage": "Body Fat %",
    "Water_Intake (liters)": "Water Intake",
    "Workout_Frequency (days/week)": "Workout Frequency",
    "Experience_Level": "Experience Level",
    "BMI": "BMI",
    "Gender_enc": "Gender",
    "Workout_enc": "Workout Type",
}

GENDER_MAP = {"male": 1, "female": 0}
WORKOUT_MAP = {"cardio": 0, "strength": 1, "yoga": 2, "hiit": 3}

NUMERIC_INPUT_SPECS = {
    "Age": (18, 100),
    "Weight (kg)": (30, 250),
    "Height (m)": (1.2, 2.4),
    "Max_BPM": (80, 240),
    "Avg_BPM": (40, 220),
    "Resting_BPM": (30, 130),
    "Session_Duration (hours)": (0.1, 6.0),
    "Calories_Burned": (0, 4000),
    "Fat_Percentage": (3, 70),
    "Water_Intake (liters)": (0, 8),
    "Workout_Frequency (days/week)": (0, 7),
    "Experience_Level": (1, 3),
    "BMI": (10, 60),
}

OPTIONAL_NUMERIC_FIELDS = {"Target_Practical_Score": (0, 100)}
