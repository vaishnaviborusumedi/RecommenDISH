import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from main import app

# Use separate in-memory DB for tests
TEST_DATABASE_URL = "sqlite:///./test_recommandish.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def db():
    database = TestingSessionLocal()
    yield database
    database.close()


@pytest.fixture(scope="session")
def sample_user(client):
    payload = {
        "name": "Test User",
        "email": "testuser@test.com",
        "age": 25,
        "weight_kg": 70.0,
        "height_cm": 175.0,
        "sex": "male",
        "activity_level": 3,
        "goal": "maintain",
        "allergies": "",
        "conditions": ""
    }
    r = client.post("/api/v1/users/", json=payload)
    return r.json()


@pytest.fixture(scope="session")
def sample_food(db):
    from app.db.models import Food
    food = Food(
        name="Test Chicken", category="protein",
        calories=165, protein_g=31, carbs_g=0,
        fat_g=3.6, fiber_g=0, sugar_g=0,
        sodium_mg=74, is_vegetarian=False,
        is_vegan=False, is_gluten_free=True
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return food