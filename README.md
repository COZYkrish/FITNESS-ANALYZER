# 🏋️ Fitness Habit Analyzer

A production-grade end-to-end Machine Learning web application with a dark futuristic glassmorphism UI.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train all ML models
python train_model.py

# 3. Start the Flask server
python app.py

# 4. Open browser
# http://127.0.0.1:5000
```

## 🧠 ML Models

| Model | Algorithm | Target | Performance |
|-------|-----------|--------|-------------|
| Regression | RandomForestRegressor (200 trees) | Fitness Score (0–100) | R² = 0.9156 |
| Classification | LogisticRegression | Fit / Average / Unfit | ACC = 98.3% |
| Clustering | KMeans (k=3) | Active / Balanced / Sedentary | Silhouette = 0.054 |

## 📄 Pages

- `/` — Landing page with hero, features, and model stats
- `/dashboard` — Real-time ML prediction dashboard with all inputs
- `/progress` — Weekly progress tracking (localStorage)
- `/health` — Water tracker, BMI calculator, daily checklist
- `/analytics` — Data insights, correlation heatmap, model comparison
- `/about` — Architecture, tech stack, run instructions

## 🎯 Features

- ⚡ Real-time predictions on slider change (no submit button)
- 🧬 Explainable AI — Feature Importance chart
- 🤖 Smart AI suggestions with impact percentages
- 📊 Model comparison: Linear vs RandomForest
- 💧 Daily water intake tracker with reminders
- ⚖️ BMI calculator with Harris-Benedict calorie estimation
- 🎯 Goal tracking with progress meter
- 📈 Weekly progress charts via localStorage
- 🔥 Correlation heatmap from real dataset
- 📄 Export fitness report to file
- 🔔 Smart browser notifications

## 📁 Project Structure

```
fitness-analyzer/
├── app.py                          # Flask backend
├── train_model.py                  # ML training script
├── requirements.txt
├── README.md
├── gym_members_exercise_tracking_synthetic_data.csv
├── model/
│   ├── regression.pkl              # RandomForestRegressor
│   ├── classifier.pkl              # LogisticRegression
│   ├── clustering.pkl              # KMeans
│   ├── scaler.pkl                  # StandardScaler
│   ├── label_encoder.pkl           # LabelEncoder for fitness levels
│   ├── cluster_map.pkl             # Cluster → lifestyle mapping
│   ├── features.pkl                # Feature names list
│   └── metadata.json               # Model metrics + analytics data
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── progress.html
│   ├── health.html
│   ├── analytics.html
│   └── about.html
└── static/
    ├── style.css                   # Dark glassmorphism theme
    └── script.js                   # Shared utilities
```

## 🛠️ Tech Stack

- **Backend**: Python, Flask, scikit-learn, pandas, NumPy, joblib
- **ML**: RandomForestRegressor, LogisticRegression, KMeans, StandardScaler
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JS, Chart.js
- **Storage**: Browser localStorage for progress/checklist data
- **Fonts**: Rajdhani, Exo 2, Share Tech Mono (Google Fonts)

## 📊 Dataset

`gym_members_exercise_tracking_synthetic_data.csv` — 1,800 gym member records with 15 features:
Age, Gender, Weight, Height, Max/Avg/Resting BPM, Session Duration, Calories Burned,
Workout Type, Fat Percentage, Water Intake, Workout Frequency, Experience Level, BMI
