import numpy as np
from sqlalchemy.orm import Session

from app.db.models import User, Food, MealLog
from app.features.food_vectors import food_to_vector
from app.features.gap_features import get_nutrient_gaps
from app.ml.clustering import get_cluster_peers
from app.ml.association_rules import get_top_consequents
from app.utils.logger import logger
from config.settings import settings


def get_recent_foods(user_id: int, db: Session, days: int = 7) -> list[str]:
    """Return names of foods the user ate recently."""
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)

    logs = (
        db.query(MealLog, Food)
        .join(Food, MealLog.food_id == Food.id)
        .filter(MealLog.user_id == user_id)
        .filter(MealLog.logged_at >= cutoff)
        .all()
    )
    return list({food.name for _, food in logs})


def score_food(food: Food, gaps: dict, cluster_food_ids: set) -> float:
    """
    Score a single food for a user based on:
    - How well it fills nutrient gaps        (40%)
    - Whether cluster peers eat it           (30%)
    - Penalize if over calorie target        (30%)
    """
    score = 0.0

    # Gap filling score
    if gaps["needs_protein"] and (food.protein_g or 0) >= 15:
        score += 0.25
    if gaps["needs_fiber"] and (food.fiber_g or 0) >= 5:
        score += 0.15
    if not gaps["over_calories"]:
        score += 0.10
    else:
        # Penalize high calorie foods when over target
        if (food.calories or 0) > 300:
            score -= 0.20

    # Cluster peer popularity
    if food.id in cluster_food_ids:
        score += 0.30

    # Bonus for balanced macros (has protein + fiber)
    if (food.protein_g or 0) > 5 and (food.fiber_g or 0) > 2:
        score += 0.10

    # Small bonus for low sodium
    if (food.sodium_mg or 0) < 200:
        score += 0.05

    return round(score, 4)


def get_cluster_popular_foods(user: User, db: Session) -> set:
    """
    Get food IDs popular among cluster peers.
    Falls back to empty set if no peers.
    """
    peers = get_cluster_peers(user, db)
    if not peers:
        return set()

    peer_ids = [p.id for p in peers]
    logs = (
        db.query(MealLog)
        .filter(MealLog.user_id.in_(peer_ids))
        .all()
    )
    return {log.food_id for log in logs}


def recommend(user: User, db: Session, meal_type: str = None) -> list[dict]:
    """
    Main recommendation function.
    Returns ranked list of food recommendations with scores and reasons.
    """
    logger.info(f"Generating recommendations for user {user.id} ({user.name})")

    # 1. Get nutrient gaps
    gaps = get_nutrient_gaps(user, db)
    logger.info(f"Gaps: protein={gaps['protein_gap']}g  fiber={gaps['fiber_gap']}g  "
                f"calories={gaps['calories_gap']}kcal")

    # 2. Get recently eaten foods (avoid repetition)
    recent = get_recent_foods(user.id, db)
    logger.info(f"Recent foods: {recent}")

    # 3. Association rule candidates
    rule_candidates = get_top_consequents(recent) if recent else []
    logger.info(f"Rule candidates: {rule_candidates}")

    # 4. Cluster peer popular foods
    cluster_food_ids = get_cluster_popular_foods(user, db)
    logger.info(f"Cluster peer food IDs: {cluster_food_ids}")

    # 5. Get all foods, filter allergies
    all_foods = db.query(Food).all()
    allergies = [a.strip().lower() for a in (user.allergies or "").split(",") if a.strip()]

    filtered_foods = []
    for food in all_foods:
        name_lower = food.name.lower()
        if any(a in name_lower for a in allergies):
            continue
        filtered_foods.append(food)

    # 6. Score every food
    scored = []
    for food in filtered_foods:
        base_score = score_food(food, gaps, cluster_food_ids)

        # Lift score from association rules
        rule_boost = 0.15 if food.name in rule_candidates else 0.0

        # Recency penalty — avoid recommending same food twice in a row
        recency_penalty = -0.10 if food.name in recent else 0.0

        final_score = base_score + rule_boost + recency_penalty

        scored.append({
            "food_id":    food.id,
            "food_name":  food.name,
            "category":   food.category,
            "calories":   food.calories,
            "protein_g":  food.protein_g,
            "fiber_g":    food.fiber_g,
            "score":      round(final_score, 4),
            "rule_match": food.name in rule_candidates,
            "peer_match": food.id in cluster_food_ids,
        })

    # 7. Sort by score, return top N
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:settings.n_recommendations]

    logger.info(f"Top {len(top)} recommendations generated")
    return top


def build_recommendation_context(user: User, db: Session) -> dict:
    """
    Bundle everything the LLM needs into one context dict.
    Used in Phase 6 for the API prompt.
    """
    gaps    = get_nutrient_gaps(user, db)
    top     = recommend(user, db)
    recent  = get_recent_foods(user.id, db)

    return {
        "user": {
            "name":           user.name,
            "goal":           user.goal,
            "activity_level": user.activity_level,
            "cluster_id":     user.cluster_id,
        },
        "gaps":             gaps,
        "recent_foods":     recent,
        "recommendations":  top,
    }