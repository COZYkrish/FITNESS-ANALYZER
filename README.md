# 🏋️ Kinetic Ether

**Kinetic Ether** is a Flask-based fitness intelligence application that combines machine learning predictions, health tracking tools, analytics, and a cinematic frontend experience.

## 🌐 Live Demo

🔗 https://fitness-analyzer-two.vercel.app/

It helps users explore fitness performance through:
- 🎯 practical fitness scoring
- 🧠 fitness-level classification
- 🧬 lifestyle clustering
- 📈 progress tracking
- 💧 health utilities and reminders
- ✨ a premium interactive UI built on HTML, CSS, and vanilla JavaScript

## 🌟 Highlights

- ⚡ Real-time prediction updates from the dashboard
- 🤖 Multiple ML outputs from a single input profile
- 📊 Analytics page with model comparison, distributions, and correlation heatmap
- 🧭 Goal planner with target-gap guidance
- 💾 Progress history stored in `localStorage`
- 📄 Exportable fitness report
- 💧 Water tracker, BMI calculator, and daily checklist
- 🔔 Browser reminder support
- 🎨 Modern glassmorphism + fitness-tech visual system

## 🧠 Machine Learning Overview

The app uses three model layers:

| Model Type | Purpose | Output |
| --- | --- | --- |
| Regression | Predict overall fitness score | Continuous score |
| Classification | Label the user’s fitness band | `Fit`, `Average`, or `Unfit` |
| Clustering | Group the user by behavior profile | Lifestyle cluster |

These models are trained from the included gym-member dataset and loaded by the Flask service layer at runtime.

## 🖥️ Application Pages

| Route | Description |
| --- | --- |
| `/` | Landing page and product-story overview |
| `/dashboard` | Main prediction cockpit with live results |
| `/progress` | Saved session history and progress charts |
| `/health` | Water tracker, BMI calculator, checklist, reminders |
| `/analytics` | Dataset insights, model metrics, charts, and heatmap |
| `/about` | Product architecture and stack overview |

## ⚙️ Tech Stack

### Backend
- 🐍 Python
- 🌐 Flask
- 🧪 scikit-learn
- 🧮 pandas
- 🔢 NumPy
- 📦 joblib

### Frontend
- 🧱 HTML templates
- 🎨 CSS
- 🧭 Vanilla JavaScript
- 📉 Chart.js
- 🎞️ GSAP + ScrollTrigger

### Persistence
- 💾 Browser `localStorage` for progress and health utilities
- 🗂️ Serialized ML artifacts in `model/`

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train models

```bash
python train_model.py
```

### 3. Run the app

```bash
python app.py
```

### 4. Open in browser

```text
http://127.0.0.1:5000
```

## 📦 Core Functionality

### 🎯 Prediction Flow
- Collect user fitness and health inputs from the dashboard
- Send them to `/predict`
- Return prediction, level, lifestyle, planner output, reliability, suggestions, and validation messages
- Render the response live in the UI

### 📈 Progress Tracking
- Saves dashboard snapshots into `fitai_progress`
- Visualizes score changes and session history
- Uses browser-only persistence without changing backend behavior

### 💧 Health Utilities
- Water intake tracking
- BMI and calorie estimation
- Daily wellness checklist
- Notification-based reminder system

### 📊 Analytics
- Feature importance chart
- Model comparison metrics
- Distribution charts
- Correlation heatmap
- Lifestyle and fitness-level breakdowns

## 📁 Key Files

- `app.py` — Flask entrypoint and route definitions
- `services/prediction_service.py` — model loading, prediction orchestration, analytics payload generation
- `validators.py` — request validation for prediction input
- `train_model.py` — training pipeline for model artifacts
- `templates/` — Jinja templates for all app pages
- `static/style.css` — shared visual system and responsive UI styling
- `static/script.js` — shared interactions, reveal logic, tilt, parallax, and UI helpers
- `model/metadata.json` — analytics/model metadata used by the frontend

## 📊 Dataset

The project uses:

`gym_members_exercise_tracking_synthetic_data.csv`

It contains synthetic gym-member exercise tracking data used to train the regression, classification, and clustering models.

## 🧩 Project Structure

```text
FITNESS/
├── app.py
├── config.py
├── validators.py
├── train_model.py
├── requirements.txt
├── README.md
├── PHASE_PLAN.md
├── gym_members_exercise_tracking_synthetic_data.csv
├── model/
│   ├── regression.pkl
│   ├── classifier.pkl
│   ├── clustering.pkl
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   ├── cluster_map.pkl
│   ├── features.pkl
│   └── metadata.json
├── services/
│   ├── __init__.py
│   └── prediction_service.py
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── about.html
    ├── analytics.html
    ├── base_macros.html
    ├── base_site.html
    ├── dashboard.html
    ├── health.html
    ├── index.html
    └── progress.html
```
