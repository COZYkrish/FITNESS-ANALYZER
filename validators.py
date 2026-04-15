"""Input validation utilities for prediction requests."""

from __future__ import annotations

from typing import Any

from config import GENDER_MAP, NUMERIC_INPUT_SPECS, OPTIONAL_NUMERIC_FIELDS, WORKOUT_MAP


class ValidationError(ValueError):
    """Raised when the incoming request payload is invalid."""


def _coerce_numeric(payload: dict[str, Any], field: str, bounds: tuple[float, float]) -> float:
    if field not in payload:
        raise ValidationError(f"Missing required field: {field}")

    try:
        value = float(payload[field])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Field {field} must be numeric.") from exc

    low, high = bounds
    if value < low or value > high:
        raise ValidationError(f"Field {field} must be between {low} and {high}.")
    return value


def validate_prediction_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    cleaned: dict[str, Any] = {}
    for field, bounds in NUMERIC_INPUT_SPECS.items():
        cleaned[field] = _coerce_numeric(payload, field, bounds)

    gender = str(payload.get("Gender", "")).strip().lower()
    if gender not in GENDER_MAP:
        raise ValidationError("Gender must be one of: male, female.")
    cleaned["Gender"] = gender

    workout_type = str(payload.get("Workout_Type", "")).strip().lower()
    if workout_type not in WORKOUT_MAP:
        raise ValidationError("Workout_Type must be one of: cardio, strength, yoga, hiit.")
    cleaned["Workout_Type"] = workout_type

    for field, bounds in OPTIONAL_NUMERIC_FIELDS.items():
        if payload.get(field) in (None, ""):
            continue
        cleaned[field] = _coerce_numeric(payload, field, bounds)

    cleaned["Gender_enc"] = GENDER_MAP[gender]
    cleaned["Workout_enc"] = WORKOUT_MAP[workout_type]
    return cleaned
