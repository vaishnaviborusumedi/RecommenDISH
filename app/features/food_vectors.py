import numpy as np
from app.db.models import Food


FOOD_FEATURE_COLS = [
    "calories", "protein_g", "carbs_g", "fat_g",
    "fiber_g", "sugar_g", "sodium_mg",
    "is_vegetarian", "is_vegan", "is_gluten_free",
]

# Per-100g reference maxes for normalization
FEATURE_MAXES = {
    "calories":     900.0,
    "protein_g":     40.0,
    "carbs_g":       80.0,
    "fat_g":         60.0,
    "fiber_g":       20.0,
    "sugar_g":       30.0,
    "sodium_mg":   2000.0,
    "is_vegetarian":  1.0,
    "is_vegan":       1.0,
    "is_gluten_free": 1.0,
}


def food_to_vector(food: Food) -> np.ndarray:
    """Convert a Food ORM object to a normalized feature vector."""
    raw = {
        "calories":      food.calories or 0,
        "protein_g":     food.protein_g or 0,
        "carbs_g":       food.carbs_g or 0,
        "fat_g":         food.fat_g or 0,
        "fiber_g":       food.fiber_g or 0,
        "sugar_g":       food.sugar_g or 0,
        "sodium_mg":     food.sodium_mg or 0,
        "is_vegetarian": float(food.is_vegetarian),
        "is_vegan":      float(food.is_vegan),
        "is_gluten_free":float(food.is_gluten_free),
    }

    vector = np.array([
        raw[col] / FEATURE_MAXES[col]
        for col in FOOD_FEATURE_COLS
    ], dtype=np.float32)

    return np.clip(vector, 0.0, 1.0)


def foods_to_matrix(foods: list) -> np.ndarray:
    """Convert a list of Food objects to a 2D feature matrix."""
    return np.stack([food_to_vector(f) for f in foods])