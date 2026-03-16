import numpy as np
from app.db.models import User
from app.features.food_vectors import foods_to_matrix


def make_user(**kwargs):
    defaults = dict(
        id=99, name="ML Test", email="ml@test.com",
        age=28, weight_kg=72, height_cm=176,
        sex="male", activity_level=3, goal="maintain",
        allergies="", conditions="", cluster_id=None
    )
    defaults.update(kwargs)
    return User(**defaults)


def test_foods_matrix_shape(db):
    from app.db.models import Food
    foods = db.query(Food).all()
    if not foods:
        return
    matrix = foods_to_matrix(foods)
    assert matrix.shape == (len(foods), 10)


def test_foods_matrix_normalized(db):
    from app.db.models import Food
    foods = db.query(Food).all()
    if not foods:
        return
    matrix = foods_to_matrix(foods)
    assert matrix.min() >= 0.0
    assert matrix.max() <= 1.0


def test_recommender_returns_list(client, sample_user, db):
    from app.db.models import User as UserModel
    from app.ml.recommender import recommend
    user = db.query(UserModel).filter(
        UserModel.id == sample_user["id"]
    ).first()
    if user:
        results = recommend(user, db)
        assert isinstance(results, list)


def test_recommender_scores_between_zero_and_one(client, sample_user, db):
    from app.db.models import User as UserModel
    from app.ml.recommender import recommend
    user = db.query(UserModel).filter(
        UserModel.id == sample_user["id"]
    ).first()
    if user:
        results = recommend(user, db)
        for r in results:
            assert -1.0 <= r["score"] <= 1.5


def test_recommender_sorted_by_score(client, sample_user, db):
    from app.db.models import User as UserModel
    from app.ml.recommender import recommend
    user = db.query(UserModel).filter(
        UserModel.id == sample_user["id"]
    ).first()
    if user:
        results = recommend(user, db)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        