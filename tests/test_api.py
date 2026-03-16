def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_create_user(client):
    payload = {
        "name": "API Test User",
        "email": "apitest@test.com",
        "age": 30,
        "weight_kg": 75.0,
        "height_cm": 178.0,
        "sex": "male",
        "activity_level": 4,
        "goal": "gain_muscle",
        "allergies": "",
        "conditions": ""
    }
    r = client.post("/api/v1/users/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "API Test User"
    assert data["goal"] == "gain_muscle"
    assert "id" in data


def test_create_duplicate_user(client):
    payload = {
        "name": "Duplicate",
        "email": "apitest@test.com",
        "age": 25,
        "weight_kg": 60.0,
        "height_cm": 165.0,
        "sex": "female",
        "activity_level": 2,
        "goal": "maintain",
        "allergies": "",
        "conditions": ""
    }
    r = client.post("/api/v1/users/", json=payload)
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"]


def test_get_user(client, sample_user):
    r = client.get(f"/api/v1/users/{sample_user['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == sample_user["email"]


def test_get_user_not_found(client):
    r = client.get("/api/v1/users/99999")
    assert r.status_code == 404


def test_list_users(client):
    r = client.get("/api/v1/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_log_meal(client, sample_user, sample_food):
    payload = {
        "food_id":   sample_food.id,
        "meal_type": "lunch",
        "portion_g": 150.0,
        "rating":    4
    }
    r = client.post(f"/api/v1/meals/{sample_user['id']}", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["food_id"]   == sample_food.id
    assert data["meal_type"] == "lunch"
    assert data["portion_g"] == 150.0


def test_log_meal_invalid_user(client, sample_food):
    payload = {
        "food_id":   sample_food.id,
        "meal_type": "lunch",
        "portion_g": 100.0,
        "rating":    3
    }
    r = client.post("/api/v1/meals/99999", json=payload)
    assert r.status_code == 404


def test_get_meal_logs(client, sample_user):
    r = client.get(f"/api/v1/meals/{sample_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_browse_foods(client):
    r = client.get("/api/v1/recommend/foods/all")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_recommendations(client, sample_user):
    r = client.get(f"/api/v1/recommend/{sample_user['id']}")
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    assert "gaps" in data
    assert "llm_suggestion" in data
    assert len(data["recommendations"]) > 0


def test_recommendation_invalid_user(client):
    r = client.get("/api/v1/recommend/99999")
    assert r.status_code == 404