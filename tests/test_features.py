import numpy as np
from app.db.models import User, Food
from app.features.food_vectors import food_to_vector
from app.features.nutrition_targets import calculate_bmr, calculate_tdee, calculate_macro_targets


def make_user(**kwargs):
    defaults = dict(
        id=1, name="Test", email="t@t.com",
        age=25, weight_kg=70, height_cm=175,
        sex="male", activity_level=3, goal="maintain",
        allergies="", conditions=""
    )
    defaults.update(kwargs)
    return User(**defaults)


def make_food(**kwargs):
    defaults = dict(
        id=1, name="TestFood", category="protein",
        calories=200, protein_g=20, carbs_g=10,
        fat_g=5, fiber_g=3, sugar_g=1,
        sodium_mg=100, is_vegetarian=True,
        is_vegan=False, is_gluten_free=True
    )
    defaults.update(kwargs)
    return Food(**defaults)


def test_food_vector_shape():
    food = make_food()
    vec = food_to_vector(food)
    assert vec.shape == (10,)


def test_food_vector_normalized():
    food = make_food()
    vec = food_to_vector(food)
    assert vec.min() >= 0.0
    assert vec.max() <= 1.0


def test_food_vector_zeros_on_none():
    food = make_food(protein_g=None, fiber_g=None)
    vec = food_to_vector(food)
    assert vec[1] == 0.0  # protein index
    assert vec[4] == 0.0  # fiber index


def test_bmr_male():
    user = make_user(sex="male", weight_kg=80, height_cm=180, age=30)
    bmr = calculate_bmr(user)
    assert 1700 < bmr < 1900


def test_bmr_female():
    user = make_user(sex="female", weight_kg=60, height_cm=165, age=25)
    bmr = calculate_bmr(user)
    assert 1300 < bmr < 1600


def test_tdee_higher_for_active():
    sedentary = make_user(activity_level=1)
    active    = make_user(activity_level=5)
    assert calculate_tdee(active) > calculate_tdee(sedentary)


def test_macro_targets_keys():
    user    = make_user()
    targets = calculate_macro_targets(user)
    assert "calories"  in targets
    assert "protein_g" in targets
    assert "carbs_g"   in targets
    assert "fat_g"     in targets
    assert "fiber_g"   in targets


def test_macro_targets_positive():
    user    = make_user()
    targets = calculate_macro_targets(user)
    assert all(v > 0 for v in targets.values())


def test_gain_muscle_higher_protein():
    muscle = make_user(goal="gain_muscle")
    lose   = make_user(goal="lose_weight")
    assert calculate_macro_targets(muscle)["protein_g"] >= \
           calculate_macro_targets(lose)["protein_g"]