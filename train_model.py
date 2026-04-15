"""
Fitness Habit Analyzer - Model Training Script
Trains Regression, Classification, and Clustering models on gym dataset.
"""

import pandas as pd
import numpy as np
import joblib
import os
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (mean_squared_error, r2_score,
                              accuracy_score, classification_report,
                              silhouette_score)

# ─────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ─────────────────────────────────────────────
print("📂 Loading dataset...")
df = pd.read_csv("gym_members_exercise_tracking_synthetic_data.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Drop rows with too many nulls
df.dropna(thresh=int(len(df.columns) * 0.6), inplace=True)

# Encode Gender
df['Gender_enc'] = (df['Gender'].str.strip().str.lower() == 'male').astype(int)

# Encode Workout_Type
workout_map = {'Cardio': 0, 'Strength': 1, 'Yoga': 2, 'HIIT': 3}
df['Workout_enc'] = df['Workout_Type'].map(workout_map).fillna(0)

# Fix Max_BPM column (may have mixed types)
df['Max_BPM'] = pd.to_numeric(df['Max_BPM'], errors='coerce')

# Fill remaining numeric NaNs with median
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

print(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")

# ─────────────────────────────────────────────
# 2. ENGINEER FITNESS SCORE (target for regression)
# ─────────────────────────────────────────────
# Composite score based on multiple fitness indicators (0–100 scale)
def compute_fitness_score(row):
    score = 0.0
    # High calorie burn → good
    score += min(row['Calories_Burned'] / 2000 * 25, 25)
    # Higher session duration → good
    score += min(row['Session_Duration (hours)'] / 2.0 * 15, 15)
    # Lower fat % → good (inverse)
    score += max(0, (50 - row['Fat_Percentage']) / 50 * 20)
    # Higher workout frequency → good
    score += min(row['Workout_Frequency (days/week)'] / 7 * 15, 15)
    # Higher experience level → good
    score += min((row['Experience_Level'] - 1) / 2 * 10, 10)
    # Lower resting BPM → better cardiovascular fitness
    score += max(0, (100 - row['Resting_BPM']) / 100 * 10)
    # Higher water intake → good
    score += min(row['Water_Intake (liters)'] / 4.0 * 5, 5)
    return round(min(max(score, 0), 100), 2)

df['fitness_score'] = df.apply(compute_fitness_score, axis=1)
print(f"📊 Fitness score range: {df['fitness_score'].min():.1f} – {df['fitness_score'].max():.1f}")

# ─────────────────────────────────────────────
# 3. ENGINEER FITNESS LEVEL (target for classification)
# ─────────────────────────────────────────────
def classify_level(score):
    if score >= 65:
        return 'Fit'
    elif score >= 40:
        return 'Average'
    else:
        return 'Unfit'

df['fitness_level'] = df['fitness_score'].apply(classify_level)
print("📊 Fitness level distribution:")
print(df['fitness_level'].value_counts())

# ─────────────────────────────────────────────
# 4. DEFINE FEATURES
# ─────────────────────────────────────────────
FEATURES = [
    'Age', 'Weight (kg)', 'Height (m)', 'Max_BPM', 'Avg_BPM', 'Resting_BPM',
    'Session_Duration (hours)', 'Calories_Burned', 'Fat_Percentage',
    'Water_Intake (liters)', 'Workout_Frequency (days/week)',
    'Experience_Level', 'BMI', 'Gender_enc', 'Workout_enc'
]

X = df[FEATURES].copy()
y_reg = df['fitness_score']
y_clf = df['fitness_level']

# ─────────────────────────────────────────────
# 5. SCALING
# ─────────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

os.makedirs("model", exist_ok=True)
joblib.dump(scaler, "model/scaler.pkl")
joblib.dump(FEATURES, "model/features.pkl")
print("✅ Scaler saved")

# ─────────────────────────────────────────────
# 6. REGRESSION – RandomForest vs LinearRegression
# ─────────────────────────────────────────────
print("\n🔁 Training Regression models...")
X_tr, X_te, yr_tr, yr_te = train_test_split(X_scaled, y_reg, test_size=0.2, random_state=42)

rf_reg = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
rf_reg.fit(X_tr, yr_tr)
yr_pred_rf = rf_reg.predict(X_te)

lr_reg = LinearRegression()
lr_reg.fit(X_tr, yr_tr)
yr_pred_lr = lr_reg.predict(X_te)

rf_r2 = r2_score(yr_te, yr_pred_rf)
lr_r2 = r2_score(yr_te, yr_pred_lr)
rf_rmse = np.sqrt(mean_squared_error(yr_te, yr_pred_rf))
lr_rmse = np.sqrt(mean_squared_error(yr_te, yr_pred_lr))

print(f"  RandomForest  → R²={rf_r2:.4f}, RMSE={rf_rmse:.4f}")
print(f"  LinearReg     → R²={lr_r2:.4f}, RMSE={lr_rmse:.4f}")

joblib.dump(rf_reg, "model/regression.pkl")
print("✅ Regression model saved (RandomForestRegressor)")

# Feature importances
feat_importance = dict(zip(FEATURES, rf_reg.feature_importances_))
feat_importance_sorted = dict(sorted(feat_importance.items(), key=lambda x: x[1], reverse=True))

# ─────────────────────────────────────────────
# 7. CLASSIFICATION – Logistic Regression Used to predict the category fitness_level like Fit, Average, Unfit.
# ─────────────────────────────────────────────
print("\n🔁 Training Classification model...")
le = LabelEncoder()
y_clf_enc = le.fit_transform(y_clf)

X_tr2, X_te2, yc_tr, yc_te = train_test_split(X_scaled, y_clf_enc, test_size=0.2, random_state=42, stratify=y_clf_enc)

clf = LogisticRegression(max_iter=2000, random_state=42, C=1.0, solver='lbfgs')
clf.fit(X_tr2, yc_tr)
yc_pred = clf.predict(X_te2)

clf_acc = accuracy_score(yc_te, yc_pred)
cv_scores = cross_val_score(clf, X_scaled, y_clf_enc, cv=5, scoring='accuracy')

print(f"  Accuracy: {clf_acc:.4f}")
print(f"  CV Mean:  {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(classification_report(yc_te, yc_pred, target_names=le.classes_))

joblib.dump(clf, "model/classifier.pkl")
joblib.dump(le, "model/label_encoder.pkl")
print("✅ Classifier saved (LogisticRegression)")

# ─────────────────────────────────────────────
# 8. CLUSTERING – KMeans (3 clusters) (sedentary, balanced, active)
# ─────────────────────────────────────────────
print("\n🔁 Training Clustering model...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=20, max_iter=500)
cluster_labels = kmeans.fit_predict(X_scaled)

sil_score = silhouette_score(X_scaled, cluster_labels)
print(f"  Silhouette Score: {sil_score:.4f}")

# Map clusters to lifestyle names based on centroid characteristics
# Compute mean fitness score per cluster
df['cluster'] = cluster_labels
cluster_means = df.groupby('cluster')['fitness_score'].mean()

sorted_clusters = cluster_means.sort_values()
cluster_map = {}
labels = ['Sedentary', 'Balanced', 'Active']
for i, (cluster_id, _) in enumerate(sorted_clusters.items()):
    cluster_map[int(cluster_id)] = labels[i]

print(f"  Cluster mapping: {cluster_map}")

joblib.dump(kmeans, "model/clustering.pkl")
joblib.dump(cluster_map, "model/cluster_map.pkl")
print("✅ Clustering model saved (KMeans)")

# ─────────────────────────────────────────────
# 9. SAVE METADATA FOR ANALYTICS
# ─────────────────────────────────────────────
metadata = {
    "regression": {
        "rf_r2": round(rf_r2, 4),
        "rf_rmse": round(rf_rmse, 4),
        "lr_r2": round(lr_r2, 4),
        "lr_rmse": round(lr_rmse, 4)
    },
    "classification": {
        "accuracy": round(clf_acc, 4),
        "cv_mean": round(float(cv_scores.mean()), 4),
        "cv_std": round(float(cv_scores.std()), 4),
        "classes": list(le.classes_)
    },
    "clustering": {
        "silhouette": round(sil_score, 4),
        "cluster_map": cluster_map
    },
    "feature_importance": {k: round(float(v), 6) for k, v in feat_importance_sorted.items()},
    "dataset_stats": {
        "total_rows": len(df),
        "fitness_score_mean": round(float(df['fitness_score'].mean()), 2),
        "fitness_score_std": round(float(df['fitness_score'].std()), 2),
        "level_dist": df['fitness_level'].value_counts().to_dict(),
        "cluster_dist": df['cluster'].map(cluster_map).value_counts().to_dict(),
        "age_mean": round(float(df['Age'].mean()), 1),
        "bmi_mean": round(float(df['BMI'].mean()), 2),
        "calories_mean": round(float(df['Calories_Burned'].mean()), 1),
        "workout_freq_mean": round(float(df['Workout_Frequency (days/week)'].mean()), 2)
    }
}

# Correlation matrix for analytics
corr_features = ['Age', 'Weight (kg)', 'Fat_Percentage', 'Session_Duration (hours)',
                  'Calories_Burned', 'Workout_Frequency (days/week)', 'Experience_Level',
                  'Water_Intake (liters)', 'BMI', 'Resting_BPM', 'fitness_score']
corr_matrix = df[corr_features].corr().round(3).to_dict()
metadata['correlation'] = corr_matrix
metadata['corr_features'] = corr_features

# Distribution data for analytics charts
dist_data = {}
for col in ['fitness_score', 'Age', 'BMI', 'Calories_Burned', 'Fat_Percentage']:
    hist, edges = np.histogram(df[col].dropna(), bins=10)
    dist_data[col] = {
        'counts': hist.tolist(),
        'edges': [round(float(e), 2) for e in edges.tolist()]
    }
metadata['distributions'] = dist_data

with open("model/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("\n✅ All metadata saved to model/metadata.json")
print("\n🎉 Training complete! All models saved in model/")
print("=" * 50)
print(f"  Regression R²:       {rf_r2:.4f}")
print(f"  Classification Acc:  {clf_acc:.4f}")
print(f"  Clustering Sil:      {sil_score:.4f}")
print("=" * 50)
