from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.ml.recommender import build_recommendation_context
from app.ml.llm import get_llm_recommendation
from app.api.schemas import RecommendationResponse
from app.utils.logger import logger

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Recommendation request for user {user_id}")

    context = build_recommendation_context(user, db)
    llm_text = get_llm_recommendation(context)

    return RecommendationResponse(
        user_name=user.name,
        goal=user.goal,
        gaps=context["gaps"],
        recommendations=context["recommendations"],
        llm_suggestion=llm_text,
    )


@router.get("/foods/all")
def list_foods(db: Session = Depends(get_db)):
    from app.db.models import Food
    from app.api.schemas import FoodResponse
    foods = db.query(Food).all()
    return foods
@router.get("/mealplan/{user_id}")
def get_meal_plan(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.features.nutrition_targets import calculate_macro_targets
    from app.db.models import Food
    import random

    targets  = calculate_macro_targets(user)
    allergies = [a.strip().lower() for a in (user.allergies or "").split(",") if a.strip()]

    all_foods = db.query(Food).all()

    # Filter out allergens
    safe_foods = [
        f for f in all_foods
        if not any(a in f.name.lower() for a in allergies)
    ]

    # Group by category
    def get_cat(cats):
        return [f for f in safe_foods if f.category in cats]

    grains    = get_cat(["grain"])
    proteins  = get_cat(["protein"])
    veggies   = get_cat(["vegetable"])
    dairy     = get_cat(["dairy"])
    fruits    = get_cat(["fruit"])
    fats      = get_cat(["fat"])

    # Goal-based protein preference
    if user.goal == "gain_muscle":
        proteins = sorted(proteins, key=lambda f: f.protein_g or 0, reverse=True)
    elif user.goal == "lose_weight":
        proteins = sorted(proteins, key=lambda f: f.calories or 0)
    else:
        random.shuffle(proteins)

    def pick(pool, n):
        return random.sample(pool, min(n, len(pool))) if pool else []

    def food_str(f, portion):
        return f"{f.name} ({portion}g)"

    def meal_macros(foods_portions):
        cal = sum((f.calories or 0) * (p / 100) for f, p in foods_portions)
        pro = sum((f.protein_g or 0) * (p / 100) for f, p in foods_portions)
        return round(cal), round(pro)

    # ── Build breakfast ──────────────────────────────────────
    if user.goal == "gain_muscle":
        bf_items = pick(proteins, 1) + pick(grains, 1) + pick(dairy, 1)
        bf_notes = "High protein start to fuel muscle recovery and growth."
    elif user.goal == "lose_weight":
        bf_items = pick(grains, 1) + pick(dairy, 1) + pick(fruits, 1)
        bf_notes = "Light and filling breakfast to keep you satisfied."
    else:
        bf_items = pick(grains, 1) + pick(dairy, 1) + pick(fruits, 1)
        bf_notes = "Balanced breakfast with good carbs and protein."

    bf_portions = [(f, 150) for f in bf_items]
    bf_cal, bf_pro = meal_macros(bf_portions)

    # ── Build lunch ──────────────────────────────────────────
    if user.goal == "gain_muscle":
        lu_items = pick(proteins, 2) + pick(grains, 1) + pick(veggies, 1)
        lu_notes = "Protein-rich lunch to support muscle building."
    elif user.goal == "lose_weight":
        lu_items = pick(proteins, 1) + pick(veggies, 2) + pick(grains, 1)
        lu_notes = "High fiber, low calorie lunch to stay in deficit."
    else:
        lu_items = pick(proteins, 1) + pick(grains, 1) + pick(veggies, 1) + pick(dairy, 1)
        lu_notes = "Well-rounded meal with all macros covered."

    lu_portions = [(f, 150) for f in lu_items]
    lu_cal, lu_pro = meal_macros(lu_portions)

    # ── Build snack ──────────────────────────────────────────
    if user.goal == "gain_muscle":
        sn_items = pick(proteins, 1) + pick(fats, 1)
        sn_notes = "Dense snack to hit your protein targets."
    elif user.goal == "lose_weight":
        sn_items = pick(fruits, 1) + pick(dairy, 1)
        sn_notes = "Low calorie snack to beat hunger."
    else:
        sn_items = pick(fruits, 1) + pick(fats, 1)
        sn_notes = "Light snack to keep energy stable."

    sn_portions = [(f, 100) for f in sn_items]
    sn_cal, sn_pro = meal_macros(sn_portions)

    # ── Build dinner ─────────────────────────────────────────
    if user.goal == "gain_muscle":
        di_items = pick(proteins, 1) + pick(grains, 1) + pick(veggies, 1)
        di_notes = "Protein-forward dinner for overnight recovery."
    elif user.goal == "lose_weight":
        di_items = pick(proteins, 1) + pick(veggies, 2)
        di_notes = "Light protein and veggies to end the day clean."
    else:
        di_items = pick(proteins, 1) + pick(veggies, 1) + pick(grains, 1)
        di_notes = "Balanced dinner to round out your day."

    di_portions = [(f, 150) for f in di_items]
    di_cal, di_pro = meal_macros(di_portions)

    # ── Daily totals ─────────────────────────────────────────
    total_cal = bf_cal + lu_cal + sn_cal + di_cal
    total_pro = bf_pro + lu_pro + sn_pro + di_pro

    goal_messages = {
        "lose_weight":  f"Great plan {user.name}! Staying around {total_cal} kcal keeps you in a healthy deficit. Stay consistent and results will follow!",
        "gain_muscle":  f"Solid plan {user.name}! {total_pro}g of protein today supports muscle growth. Hit the gym and let the food do the work!",
        "maintain":     f"Perfect balance {user.name}! {total_cal} kcal keeps you right on track. Enjoy every meal!",
    }

    meal_plan = {
        "breakfast": {
            "foods":     [food_str(f, p) for f, p in bf_portions],
            "calories":  bf_cal,
            "protein_g": bf_pro,
            "notes":     bf_notes,
        },
        "lunch": {
            "foods":     [food_str(f, p) for f, p in lu_portions],
            "calories":  lu_cal,
            "protein_g": lu_pro,
            "notes":     lu_notes,
        },
        "snack": {
            "foods":     [food_str(f, p) for f, p in sn_portions],
            "calories":  sn_cal,
            "protein_g": sn_pro,
            "notes":     sn_notes,
        },
        "dinner": {
            "foods":     [food_str(f, p) for f, p in di_portions],
            "calories":  di_cal,
            "protein_g": di_pro,
            "notes":     di_notes,
        },
        "daily_total": {
            "calories":  total_cal,
            "protein_g": total_pro,
            "message":   goal_messages.get(user.goal, f"Great choices today {user.name}!"),
        }
    }

    return {
        "user_name":  user.name,
        "goal":       user.goal,
        "targets":    targets,
        "meal_plan":  meal_plan,
    }
@router.get("/dashboard/{user_id}")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.features.nutrition_targets import calculate_macro_targets
    from app.db.models import MealLog, Food
    from datetime import datetime, timedelta
    from sqlalchemy import func

    targets = calculate_macro_targets(user)

    # Last 7 days logs
    seven_days_ago = datetime.now() - timedelta(days=7)
    logs = (
        db.query(MealLog, Food)
        .join(Food, MealLog.food_id == Food.id)
        .filter(MealLog.user_id == user_id)
        .filter(MealLog.logged_at >= seven_days_ago)
        .order_by(MealLog.logged_at)
        .all()
    )

    # Group by date
    from collections import defaultdict
    daily = defaultdict(lambda: {
        "calories": 0, "protein": 0,
        "carbs": 0, "fat": 0, "fiber": 0
    })

    category_counts = defaultdict(int)
    meal_type_counts = defaultdict(int)
    top_foods = defaultdict(int)

    for log, food in logs:
        date_str = log.logged_at.strftime("%a %d %b")
        ratio    = (log.portion_g or 100) / 100.0
        daily[date_str]["calories"] += round((food.calories  or 0) * ratio)
        daily[date_str]["protein"]  += round((food.protein_g or 0) * ratio)
        daily[date_str]["carbs"]    += round((food.carbs_g   or 0) * ratio)
        daily[date_str]["fat"]      += round((food.fat_g     or 0) * ratio)
        daily[date_str]["fiber"]    += round((food.fiber_g   or 0) * ratio)
        category_counts[food.category or "other"] += 1
        meal_type_counts[log.meal_type or "other"] += 1
        top_foods[food.name] += 1

    # Average intake
    n = len(daily) or 1
    avg_calories = round(sum(d["calories"] for d in daily.values()) / n)
    avg_protein  = round(sum(d["protein"]  for d in daily.values()) / n)
    avg_carbs    = round(sum(d["carbs"]    for d in daily.values()) / n)
    avg_fat      = round(sum(d["fat"]      for d in daily.values()) / n)

    # BMI
    bmi = None
    bmi_category = "N/A"
    if user.weight_kg and user.height_cm:
        bmi = round(user.weight_kg / ((user.height_cm / 100) ** 2), 1)
        if   bmi < 18.5: bmi_category = "Underweight"
        elif bmi < 25.0: bmi_category = "Normal"
        elif bmi < 30.0: bmi_category = "Overweight"
        else:            bmi_category = "Obese"

    return {
        "user_name":        user.name,
        "goal":             user.goal,
        "bmi":              bmi,
        "bmi_category":     bmi_category,
        "targets":          targets,
        "avg_intake": {
            "calories": avg_calories,
            "protein":  avg_protein,
            "carbs":    avg_carbs,
            "fat":      avg_fat,
        },
        "daily_calories":   dict(daily),
        "category_counts":  dict(category_counts),
        "meal_type_counts": dict(meal_type_counts),
        "top_foods":        dict(sorted(
                                top_foods.items(),
                                key=lambda x: x[1],
                                reverse=True
                            )[:5]),
    }
@router.get("/recipe/{user_id}")
def get_recipe(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.ml.recommender import recommend
    from app.db.models import Food
    import random

    # Get top recommended foods for this user
    recs      = recommend(user, db)
    top_foods = [r["food_name"] for r in recs[:3]]

    if not top_foods:
        raise HTTPException(status_code=404, detail="No recommendations found")

    # Get all foods for ingredients pool
    all_foods  = db.query(Food).all()
    food_names = [f.name for f in all_foods]

    # Indian cooking styles based on goal
    styles = {
        "lose_weight":  ["steamed", "grilled", "boiled", "stir-fried with minimal oil"],
        "gain_muscle":  ["high-protein", "pan-fried", "baked", "pressure-cooked"],
        "maintain":     ["traditional", "home-style", "balanced", "lightly spiced"],
    }
    cooking_style = random.choice(
        styles.get(user.goal, ["home-style"])
    )

    # Common Indian spices and condiments always available
    pantry = [
        "turmeric", "cumin seeds", "mustard seeds", "coriander powder",
        "garam masala", "red chilli powder", "ginger", "garlic",
        "onion", "tomato", "curry leaves", "salt", "oil",
        "green chillies", "fresh coriander"
    ]

    # Build recipe using rule-based logic — no LLM needed
    recipes = {
        "Dal Tadka": {
            "name":        "Dal Tadka",
            "description": "A comforting Indian lentil dish tempered with aromatic spices.",
            "ingredients": [
                "1 cup Dal Tadka (200g)",
                "2 tbsp oil",
                "1 tsp cumin seeds",
                "1 onion, finely chopped",
                "2 tomatoes, chopped",
                "1 tsp turmeric",
                "1 tsp red chilli powder",
                "1 tsp garam masala",
                "Salt to taste",
                "Fresh coriander for garnish"
            ],
            "steps": [
                "Wash and pressure cook lentils with turmeric and salt for 3 whistles.",
                "Heat oil in a pan, add cumin seeds and let them splutter.",
                "Add onions and sauté until golden brown.",
                "Add tomatoes, red chilli powder and cook until oil separates.",
                "Pour the tempering over cooked lentils and mix well.",
                "Garnish with fresh coriander and serve hot with roti or rice."
            ],
            "prep_time": "10 mins",
            "cook_time": "20 mins",
            "calories":   198,
            "protein_g":  12,
            "fiber_g":    8,
            "tip":        "Add a squeeze of lemon at the end for extra flavour."
        },
        "Palak Paneer": {
            "name":        "Palak Paneer",
            "description": "Creamy spinach curry with soft paneer cubes — a North Indian classic.",
            "ingredients": [
                "200g Paneer, cubed",
                "2 cups Saag/Spinach, blanched",
                "1 onion, chopped",
                "2 tomatoes, chopped",
                "1 tsp ginger-garlic paste",
                "1 tsp cumin seeds",
                "1 tsp garam masala",
                "2 tbsp oil",
                "Salt to taste",
                "1 tbsp fresh cream (optional)"
            ],
            "steps": [
                "Blanch spinach in hot water for 2 minutes, then blend into a smooth paste.",
                "Heat oil, add cumin seeds, onion and cook until golden.",
                "Add ginger-garlic paste and tomatoes, cook until soft.",
                "Add spinach puree, season with spices, simmer for 5 minutes.",
                "Add paneer cubes and cook for another 3 minutes.",
                "Finish with cream if desired and serve with roti."
            ],
            "prep_time": "15 mins",
            "cook_time": "20 mins",
            "calories":   220,
            "protein_g":  10,
            "fiber_g":    4,
            "tip":        "Don't overcook spinach — it loses its vibrant green colour."
        },
        "Chana Masala": {
            "name":        "Chana Masala",
            "description": "Spiced chickpea curry packed with protein and fibre.",
            "ingredients": [
                "1.5 cups Chana Masala (chickpeas, 250g)",
                "1 large onion, finely chopped",
                "2 tomatoes, pureed",
                "1 tsp ginger-garlic paste",
                "1 tsp cumin seeds",
                "1 tsp coriander powder",
                "1 tsp chana masala powder",
                "Half tsp turmeric",
                "2 tbsp oil",
                "Salt and lemon juice to taste"
            ],
            "steps": [
                "Soak chickpeas overnight, pressure cook for 4 whistles.",
                "Heat oil, add cumin seeds and onion, sauté until golden.",
                "Add ginger-garlic paste, tomato puree and all spices.",
                "Cook masala until oil separates from the mixture.",
                "Add cooked chickpeas and 1 cup water, simmer 10 minutes.",
                "Finish with lemon juice and serve with bhature or rice."
            ],
            "prep_time": "10 mins",
            "cook_time": "25 mins",
            "calories":   270,
            "protein_g":  14,
            "fiber_g":    12,
            "tip":        "Add a tea bag while boiling chickpeas for a darker colour."
        },
        "Chicken Curry": {
            "name":        "Indian Chicken Curry",
            "description": "Classic home-style chicken curry with aromatic spices.",
            "ingredients": [
                "300g Chicken Breast, cut into pieces",
                "1 large onion, finely chopped",
                "2 tomatoes, pureed",
                "1 tsp ginger-garlic paste",
                "1 tsp turmeric",
                "1 tsp red chilli powder",
                "1 tsp garam masala",
                "1 tsp coriander powder",
                "2 tbsp oil",
                "Salt to taste",
                "Fresh coriander to garnish"
            ],
            "steps": [
                "Marinate chicken with turmeric, chilli powder and salt for 15 mins.",
                "Heat oil in a deep pan, add onions and cook until golden.",
                "Add ginger-garlic paste and tomato puree, cook until oil separates.",
                "Add coriander powder, garam masala and mix well.",
                "Add marinated chicken and cook on high heat for 5 minutes.",
                "Add water, cover and simmer for 20 minutes until chicken is cooked.",
                "Garnish with coriander and serve with rice or roti."
            ],
            "prep_time": "15 mins",
            "cook_time": "30 mins",
            "calories":   240,
            "protein_g":  25,
            "fiber_g":    2,
            "tip":        "Use bone-in chicken for richer flavour."
        },
        "Rajma": {
            "name":        "Rajma Chawal",
            "description": "Hearty kidney bean curry served with steamed basmati rice.",
            "ingredients": [
                "1 cup Rajma (kidney beans, 200g)",
                "1 cup Basmati Rice (150g)",
                "1 onion, chopped",
                "2 tomatoes, pureed",
                "1 tsp ginger-garlic paste",
                "1 tsp rajma masala",
                "1 tsp cumin seeds",
                "Half tsp turmeric",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "steps": [
                "Soak rajma overnight and pressure cook for 6 whistles.",
                "Cook basmati rice separately with a pinch of salt.",
                "Heat oil, add cumin seeds and chopped onion, cook golden.",
                "Add ginger-garlic paste, tomato puree and rajma masala.",
                "Cook until oil separates, add rajma with its water.",
                "Simmer for 15 minutes until thick and creamy.",
                "Serve hot rajma over steamed rice."
            ],
            "prep_time": "10 mins",
            "cook_time": "30 mins",
            "calories":   260,
            "protein_g":  15,
            "fiber_g":    13,
            "tip":        "Mash a few beans to make the gravy naturally thick."
        },
        "Paneer Bhurji": {
            "name":        "Paneer Bhurji",
            "description": "Scrambled paneer with onions, tomatoes and spices — quick and protein-rich.",
            "ingredients": [
                "200g Paneer, crumbled",
                "1 onion, finely chopped",
                "1 tomato, chopped",
                "1 tsp cumin seeds",
                "Half tsp turmeric",
                "Half tsp red chilli powder",
                "1 tbsp oil",
                "Salt to taste",
                "Fresh coriander to garnish"
            ],
            "steps": [
                "Heat oil in a pan, add cumin seeds and let them splutter.",
                "Add onion and cook until translucent.",
                "Add tomato, turmeric, chilli powder and cook until soft.",
                "Add crumbled paneer and mix gently.",
                "Cook for 3-4 minutes on medium heat.",
                "Garnish with fresh coriander and serve with roti."
            ],
            "prep_time": "5 mins",
            "cook_time": "10 mins",
            "calories":   260,
            "protein_g":  14,
            "fiber_g":    2,
            "tip":        "Don't overcook paneer or it becomes rubbery."
        },
        "Moong Dal": {
            "name":        "Moong Dal Khichdi",
            "description": "Light and nutritious rice-lentil porridge — perfect comfort food.",
            "ingredients": [
                "Half cup Moong Dal (100g)",
                "Half cup Basmati Rice (80g)",
                "1 tsp cumin seeds",
                "Half tsp turmeric",
                "1 tbsp ghee or oil",
                "Salt to taste",
                "Fresh ginger, grated"
            ],
            "steps": [
                "Wash moong dal and rice together, soak for 15 minutes.",
                "Heat ghee in a pressure cooker, add cumin seeds.",
                "Add grated ginger and sauté for 30 seconds.",
                "Add dal-rice mixture, turmeric, salt and 3 cups water.",
                "Pressure cook for 3 whistles until soft and mushy.",
                "Serve hot with a drizzle of ghee and pickle on the side."
            ],
            "prep_time": "5 mins",
            "cook_time": "15 mins",
            "calories":   180,
            "protein_g":  14,
            "fiber_g":    9,
            "tip":        "Add a pinch of asafoetida for better digestion."
        },
        "Sprouts": {
            "name":        "Sprouts Chaat",
            "description": "Fresh and tangy sprouted moong salad — high protein, zero cooking.",
            "ingredients": [
                "1 cup Sprouts (150g)",
                "1 small onion, finely chopped",
                "1 tomato, chopped",
                "1 green chilli, chopped",
                "Half tsp chaat masala",
                "Half tsp cumin powder",
                "Lemon juice to taste",
                "Salt to taste",
                "Fresh coriander"
            ],
            "steps": [
                "Steam sprouts lightly for 2 minutes or use raw for crunch.",
                "Mix sprouts with onion, tomato and green chilli.",
                "Add chaat masala, cumin powder and salt.",
                "Squeeze lemon juice generously.",
                "Toss everything together and garnish with coriander.",
                "Serve immediately for best taste and texture."
            ],
            "prep_time": "5 mins",
            "cook_time": "2 mins",
            "calories":   99,
            "protein_g":  9,
            "fiber_g":    6,
            "tip":        "Sprout moong beans at home — soak overnight, drain and keep covered for 24 hrs."
        },
    }

    # Find matching recipe from top recommended foods
    selected_recipe = None
    for food_name in top_foods:
        if food_name in recipes:
            selected_recipe = recipes[food_name]
            break

    # Fallback — pick any recipe if no match
    if not selected_recipe:
        selected_recipe = random.choice(list(recipes.values()))

    # Add personalized tip based on goal
    goal_tips = {
        "lose_weight":  "For weight loss: reduce oil by half and increase vegetable portions.",
        "gain_muscle":  "For muscle gain: add an extra serving of protein and eat within 30 mins of workout.",
        "maintain":     "For maintenance: follow the recipe as is for a perfectly balanced meal.",
    }

    return {
        "user_name":        user.name,
        "goal":             user.goal,
        "based_on_foods":   top_foods,
        "cooking_style":    cooking_style,
        "recipe":           selected_recipe,
        "goal_tip":         goal_tips.get(user.goal, ""),
    }