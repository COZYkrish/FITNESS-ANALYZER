# Fitness Analyzer Build Plan

## Phase 1: Backend Foundation
- Extract prediction, scoring, and analytics logic out of `app.py`
- Add structured request validation and cleaner error handling
- Keep all existing pages and frontend behavior working
- Deliverables:
  - `config.py`
  - `validators.py`
  - `services/prediction_service.py`
  - thin Flask routes in `app.py`

## Phase 2: Persistent Progress
- Replace browser-only session history with SQLite-backed storage
- Add saved snapshots, comparisons, and baseline tracking
- Deliverables:
  - database schema
  - save/list/compare APIs
  - progress page backed by server data

## Phase 3: Multi-Score Health Model
- Split one score into sub-scores: training, recovery, body composition, cardio
- Rework UI to show radar/stacked score composition
- Deliverables:
  - updated training pipeline
  - new prediction schema
  - redesigned dashboard score card

## Phase 4: True Explainability and Simulation
- Add local per-user explanation instead of only static global importance
- Add scenario simulation and “apply this plan” controls
- Deliverables:
  - local feature contribution endpoint
  - what-if comparison flow
  - projected score deltas

## Phase 5: Accounts, Data Quality, and Testing
- Add auth/profile layer if desired
- Add unit/API tests and model-version checks
- Add out-of-distribution warnings and reliability guards
- Deliverables:
  - test suite
  - user profile persistence
  - stronger production safeguards
