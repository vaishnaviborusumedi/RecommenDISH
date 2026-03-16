from app.db.models import User


def calculate_bmr(user: User) -> float:
    """Mifflin-St Jeor equation."""
    if user.sex == "male":
        return 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
    else:
        return 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161


ACTIVITY_MULTIPLIERS = {
    1: 1.2,   # sedentary
    2: 1.375, # light
    3: 1.55,  # moderate
    4: 1.725, # active
    5: 1.9    # very active
}

GOAL_ADJUSTMENTS = {
    "lose_weight":   -500,
    "maintain":         0,
    "gain_muscle":   +300,
}


def calculate_tdee(user: User) -> float:
    """Total Daily Energy Expenditure."""
    bmr = calculate_bmr(user)
    multiplier = ACTIVITY_MULTIPLIERS.get(user.activity_level, 1.55)
    adjustment = GOAL_ADJUSTMENTS.get(user.goal, 0)
    return round(bmr * multiplier + adjustment, 1)


def calculate_macro_targets(user: User) -> dict:
    """
    Returns daily macro targets in grams based on goal.
    Protein-first approach for muscle gain, deficit for weight loss.
    """
    tdee = calculate_tdee(user)

    if user.goal == "gain_muscle":
        protein_g  = round(user.weight_kg * 2.2, 1)
        fat_g      = round(tdee * 0.25 / 9, 1)
        carbs_g    = round((tdee - protein_g * 4 - fat_g * 9) / 4, 1)

    elif user.goal == "lose_weight":
        protein_g  = round(user.weight_kg * 2.0, 1)
        fat_g      = round(tdee * 0.30 / 9, 1)
        carbs_g    = round((tdee - protein_g * 4 - fat_g * 9) / 4, 1)

    else:  # maintain
        protein_g  = round(user.weight_kg * 1.8, 1)
        fat_g      = round(tdee * 0.30 / 9, 1)
        carbs_g    = round((tdee - protein_g * 4 - fat_g * 9) / 4, 1)

    return {
        "calories": tdee,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fiber_g": 30.0,
    }