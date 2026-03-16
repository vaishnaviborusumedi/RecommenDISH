from sqlalchemy.orm import Session
from app.db.models import User
from app.features.nutrition_targets import calculate_macro_targets
from app.features.user_vectors import get_user_intake_stats


def get_nutrient_gaps(user: User, db: Session) -> dict:
    """
    Returns today's remaining nutrient budget.
    Positive = still needed, Negative = over target.
    """
    targets = calculate_macro_targets(user)
    intake  = get_user_intake_stats(user.id, db)

    gaps = {
        "calories_gap":  round(targets["calories"]  - intake["avg_calories"], 1),
        "protein_gap":   round(targets["protein_g"] - intake["avg_protein"],  1),
        "carbs_gap":     round(targets["carbs_g"]   - intake["avg_carbs"],    1),
        "fat_gap":       round(targets["fat_g"]     - intake["avg_fat"],      1),
        "fiber_gap":     round(targets["fiber_g"]   - intake["avg_fiber"],    1),
    }

    # Severity flags for the LLM prompt later
    gaps["needs_protein"] = gaps["protein_gap"] > 20
    gaps["needs_fiber"]   = gaps["fiber_gap"]   > 8
    gaps["over_calories"] = gaps["calories_gap"] < -200

    return gaps