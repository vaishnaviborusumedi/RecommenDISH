import numpy as np
from sqlalchemy.orm import Session
from app.db.models import User, MealLog, Food
from app.features.nutrition_targets import calculate_macro_targets


def get_user_intake_stats(user_id: int, db: Session) -> dict:
    """
    Compute average daily intake from the last 30 days of meal logs.
    Returns per-nutrient averages.
    """
    logs = (
        db.query(MealLog, Food)
        .join(Food, MealLog.food_id == Food.id)
        .filter(MealLog.user_id == user_id)
        .all()
    )

    if not logs:
        return {
            "avg_calories": 0, "avg_protein": 0,
            "avg_carbs": 0, "avg_fat": 0, "avg_fiber": 0,
            "meal_count": 0, "unique_foods": 0,
        }

    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
    food_ids = set()

    for log, food in logs:
        ratio = (log.portion_g or 100) / 100.0
        totals["calories"] += (food.calories or 0) * ratio
        totals["protein"]  += (food.protein_g or 0) * ratio
        totals["carbs"]    += (food.carbs_g or 0) * ratio
        totals["fat"]      += (food.fat_g or 0) * ratio
        totals["fiber"]    += (food.fiber_g or 0) * ratio
        food_ids.add(food.id)

    n = len(logs)
    return {
        "avg_calories":  round(totals["calories"] / n, 1),
        "avg_protein":   round(totals["protein"] / n, 1),
        "avg_carbs":     round(totals["carbs"] / n, 1),
        "avg_fat":       round(totals["fat"] / n, 1),
        "avg_fiber":     round(totals["fiber"] / n, 1),
        "meal_count":    n,
        "unique_foods":  len(food_ids),
    }


def user_to_vector(user: User, db: Session) -> np.ndarray:
    """
    Build clustering feature vector for a user.
    Combines demographics + goal encoding + intake gaps.
    """
    targets = calculate_macro_targets(user)
    intake  = get_user_intake_stats(user.id, db)

    # Gaps: how far is actual intake from target (normalized)
    cal_gap     = (targets["calories"]  - intake["avg_calories"])  / 3000.0
    protein_gap = (targets["protein_g"] - intake["avg_protein"])   / 100.0
    carbs_gap   = (targets["carbs_g"]   - intake["avg_carbs"])     / 300.0
    fat_gap     = (targets["fat_g"]     - intake["avg_fat"])       / 100.0
    fiber_gap   = (targets["fiber_g"]   - intake["avg_fiber"])     / 40.0

    # Goal encoding
    goal_map = {"lose_weight": 0.0, "maintain": 0.5, "gain_muscle": 1.0}
    goal_enc = goal_map.get(user.goal, 0.5)

    # Activity normalized
    activity_norm = (user.activity_level or 3) / 5.0

    # BMI normalized
    if user.weight_kg and user.height_cm:
        bmi = user.weight_kg / ((user.height_cm / 100) ** 2)
        bmi_norm = np.clip((bmi - 15) / 25.0, 0.0, 1.0)
    else:
        bmi_norm = 0.5

    # Diet variety (normalized)
    variety = np.clip(intake["unique_foods"] / 20.0, 0.0, 1.0)

    vector = np.array([
        goal_enc,
        activity_norm,
        bmi_norm,
        np.clip(cal_gap, -1, 1),
        np.clip(protein_gap, -1, 1),
        np.clip(carbs_gap, -1, 1),
        np.clip(fat_gap, -1, 1),
        np.clip(fiber_gap, -1, 1),
        variety,
    ], dtype=np.float32)

    return vector