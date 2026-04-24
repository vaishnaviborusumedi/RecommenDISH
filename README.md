# 🍽️ RecommenDISH

> **Smart Food & Nutrition Recommendation System**
> Personalised Indian meal recommendations powered by Machine Learning, Association Rules and AI

[![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)

---

## 📌 Overview

RecommenDISH solves a fundamental problem with generic diet apps — they give everyone the same advice. Every person has different calorie needs based on their age, weight, height, sex, activity level and health goal.

RecommenDISH calculates your exact daily nutrient targets, tracks what you eat, finds the gap between what you need and what you consumed, and recommends specific Indian foods to fill those gaps — powered by K-Means clustering, Apriori association rules and the Anthropic Claude LLM.

---

## 🌐 Live Demo

| Service | URL |
|---|---|
| Frontend | https://recommandish-frontend.onrender.com |
| API Docs | https://recommendish.onrender.com/docs |
| Health Check | https://recommendish.onrender.com/health |

---

## ✨ Features

- **Personalised Recommendations** — ML-scored food suggestions based on your exact nutrient gaps
- **K-Means Clustering** — Groups users by nutrition profile to leverage peer eating patterns
- **Apriori Association Rules** — Discovers food pairing patterns from meal logs (229+ rules mined)
- **Full Day Meal Plan** — Generates Breakfast + Lunch + Snack + Dinner tailored to your goal
- **Nutrition Dashboard** — Weekly calorie chart, macro split, food category breakdown and more
- **Recipe Suggestions** — Personalised Indian recipes with ingredients, method, chef tips
- **AI Explanations** — Claude LLM generates natural language meal suggestions
- **49 Indian Foods** — Dal Tadka, Palak Paneer, Idli, Biryani, Tandoori Chicken and more
- **Admin Panel** — Full CRUD for foods, users and meal logs directly from the UI
- **REST API** — 10+ FastAPI endpoints with auto-generated Swagger docs

---

## 🏗️ Architecture

```
User Request
     │
     ▼
Streamlit Frontend (Port 8501)
     │  HTTP requests
     ▼
FastAPI Backend (Port 8000)
     │
     ├── Feature Engineering
     │   ├── Mifflin-St Jeor BMR calculation
     │   ├── Food vectors (10-dimensional normalized)
     │   ├── User vectors (9-dimensional for clustering)
     │   └── Real-time nutrient gap features
     │
     ├── ML Layer
     │   ├── K-Means Clustering (5 clusters)
     │   ├── Apriori Association Rules (min_support=0.05)
     │   └── Recommendation scoring engine
     │
     ├── LLM Layer
     │   └── Anthropic Claude API (natural language output)
     │
     └── Database
         └── SQLAlchemy + SQLite (4 tables)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| ML | scikit-learn (K-Means), mlxtend (Apriori) |
| Database | SQLAlchemy, SQLite |
| AI | Anthropic Claude API |
| Data | USDA FoodData Central, OpenFoodFacts |
| Deployment | Render.com |
| Testing | pytest (27 tests) |

---

## 📁 Project Structure

```
RecommenDISH/
│
├── main.py                     # FastAPI app entry point
├── requirements.txt            # All dependencies
├── .env.example                # Environment variables template
├── render.yaml                 # Render deployment config
├── runtime.txt                 # Python version for Render
│
├── config/
│   └── settings.py             # Centralised configuration (pydantic-settings)
│
├── app/
│   ├── db/
│   │   ├── database.py         # SQLAlchemy engine and session
│   │   ├── models.py           # User, Food, MealLog, Recommendation tables
│   │   └── init_db.py          # Table creation + food seeding
│   │
│   ├── features/
│   │   ├── nutrition_targets.py  # BMR, TDEE, macro target calculation
│   │   ├── food_vectors.py       # Food → normalized numpy vector
│   │   ├── user_vectors.py       # User → clustering feature vector
│   │   └── gap_features.py       # Real-time nutrient gap calculation
│   │
│   ├── ml/
│   │   ├── clustering.py         # K-Means training and prediction
│   │   ├── association_rules.py  # Apriori rule mining
│   │   ├── recommender.py        # Scoring and ranking engine
│   │   ├── llm.py                # Anthropic Claude integration
│   │   ├── trainer.py            # Single entry point for retraining
│   │   └── saved_models/         # Persisted joblib model files
│   │
│   ├── api/
│   │   ├── schemas.py            # Pydantic request/response models
│   │   ├── users.py              # User CRUD endpoints
│   │   ├── meals.py              # Meal log endpoints
│   │   └── recommendations.py   # Recommendations, meal plan, recipe, dashboard
│   │
│   └── utils/
│       └── logger.py             # Loguru structured logging
│
├── frontend/
│   └── app.py                  # Streamlit 9-page UI
│
├── tests/
│   ├── conftest.py             # Test fixtures and DB override
│   ├── test_api.py             # 13 API endpoint tests
│   ├── test_features.py        # 9 feature engineering tests
│   └── test_ml.py              # 5 ML pipeline tests
│
└── data/
    ├── raw/                    # Raw data files
    └── processed/              # Processed data files
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/vaishnaviborusumedi/RecommenDISH.git
cd RecommenDISH
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your values:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=sqlite:///./recommandish.db
APP_ENV=development
DEBUG=true
SECRET_KEY=your_secret_key_here
```

### 5. Start the API

```bash
uvicorn main:app --reload
```

The API starts at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 6. Start the Frontend

Open a second terminal:

```bash
streamlit run frontend/app.py
```

Frontend opens at `http://localhost:8501`

---

## 🔌 API Endpoints

### Users
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/users/` | Create new user |
| GET | `/api/v1/users/` | List all users |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user and meal logs |

### Meals
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/meals/{user_id}` | Log a meal |
| GET | `/api/v1/meals/{user_id}` | Get meal logs |
| DELETE | `/api/v1/meals/{meal_id}` | Delete one log |
| DELETE | `/api/v1/meals/user/{id}/all` | Delete all logs |

### Recommendations
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/recommend/{user_id}` | Get food recommendations |
| GET | `/api/v1/recommend/mealplan/{user_id}` | Get full day meal plan |
| GET | `/api/v1/recommend/dashboard/{user_id}` | Get analytics data |
| GET | `/api/v1/recommend/recipe/{user_id}` | Get recipe suggestion |
| GET | `/api/v1/recommend/foods/all` | List all foods |
| POST | `/api/v1/recommend/foods/add` | Add new food |
| PUT | `/api/v1/recommend/foods/{id}` | Update food |
| DELETE | `/api/v1/recommend/foods/{id}` | Delete food |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/recommend/admin/retrain` | Retrain ML models |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_api.py::test_root                           PASSED
tests/test_api.py::test_create_user                    PASSED
tests/test_api.py::test_get_recommendations            PASSED
tests/test_features.py::test_food_vector_shape         PASSED
tests/test_features.py::test_bmr_male                  PASSED
tests/test_ml.py::test_recommender_sorted_by_score     PASSED
...
27 passed in 0.84s
```

---

## 🧠 How the ML Works

### 1. Feature Engineering

The system uses the **Mifflin-St Jeor equation** to calculate Basal Metabolic Rate:

- Male: `(10 × weight) + (6.25 × height) − (5 × age) + 5`
- Female: `(10 × weight) + (6.25 × height) − (5 × age) − 161`

TDEE (Total Daily Energy Expenditure) = BMR × activity multiplier

Goal adjustments: -500 kcal (lose weight), +300 kcal (gain muscle), 0 (maintain)

### 2. K-Means Clustering

Users are represented as 9-dimensional vectors:

```
[goal_encoding, activity_level, bmi_norm,
 calorie_gap, protein_gap, carbs_gap,
 fat_gap, fiber_gap, diet_variety]
```

K-Means groups users into 5 clusters. Cluster peers' food preferences contribute a **+0.30 score boost** to recommendations.

### 3. Apriori Association Rules

Transactions are built from daily meal logs. Rules are mined with:
- `min_support = 0.05`
- `min_confidence = 0.30`
- Sorted by **lift score** (10.0 = 10x more likely than random)

Foods appearing in rule consequents get a **+0.15 score boost**.

### 4. Recommendation Scoring

```
final_score = gap_score + cluster_boost + rule_boost - recency_penalty

Where:
  gap_score      = protein need (+0.25) + fiber need (+0.15) + calorie balance (+0.10)
  cluster_boost  = +0.30 if food popular among cluster peers
  rule_boost     = +0.15 if food in association rule consequents
  recency_penalty= -0.10 if food eaten recently
```

---

## 📊 Database Schema

```sql
users        — id, name, email, age, weight_kg, height_cm, sex,
               activity_level, goal, allergies, conditions, cluster_id

foods        — id, name, category, calories, protein_g, carbs_g, fat_g,
               fiber_g, sugar_g, sodium_mg, vitamins, minerals,
               is_vegetarian, is_vegan, is_gluten_free

meal_logs    — id, user_id, food_id, meal_type, portion_g, rating, logged_at

recommendations — id, user_id, food_id, score, reason, was_accepted, created_at
```

---

## 🍱 Food Database

49 foods across 6 categories sourced from USDA FoodData Central and OpenFoodFacts:

| Category | Examples |
|---|---|
| Protein | Chicken Breast, Dal Tadka, Chana Masala, Rajma, Paneer, Eggs, Salmon, Sprouts |
| Grain | Basmati Rice, Roti, Paratha, Idli, Dosa, Poha, Oats, Brown Rice |
| Vegetable | Palak Paneer, Aloo Gobi, Bhindi Masala, Broccoli, Spinach, Saag |
| Dairy | Curd, Lassi, Buttermilk, Greek Yogurt, Paneer |
| Fruit | Banana, Mango, Guava, Papaya |
| Fat | Almonds, Coconut Chutney |

---

## 🖥️ Frontend Pages

| Page | Description |
|---|---|
| 🏠 Home | User overview with avatar cards, activity bars, goal badges |
| ✨ Recommendations | ML-scored food recommendations with nutrient gap analysis |
| 🗓️ Meal Plan | Full day Indian meal plan with calorie gauge chart |
| 📊 Dashboard | Weekly charts, macro split, food category breakdown |
| 👨‍🍳 Recipes | Personalised Indian recipes with ingredients and method |
| 📝 Log Meal | Log any food with portion and rating |
| 👤 Add User | Create new user profile |
| 🥦 Foods | Browse and filter all 49 foods |
| ⚙️ Admin | Full CRUD for foods, users, meal logs and model retraining |

---

## 🌍 Deployment

### Deploy on Render (Free)

**API Service:**
```
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn main:app --host 0.0.0.0 --port $PORT
```

Environment variables:
```
ANTHROPIC_API_KEY = your_key
DATABASE_URL      = sqlite:///./recommandish.db
APP_ENV           = production
DEBUG             = false
SECRET_KEY        = your_secret
```

**Frontend Service:**
```
Build Command:  pip install -r requirements.txt
Start Command:  streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
```

Environment variables:
```
API_URL = https://your-api-service.onrender.com/api/v1
```

---

## 📈 Future Improvements

- [ ] PostgreSQL migration for production scale
- [ ] User authentication with JWT
- [ ] Daily retraining cron job
- [ ] Water intake tracker
- [ ] Export weekly nutrition report as PDF
- [ ] Mobile app with React Native
- [ ] OpenFoodFacts live API integration
- [ ] Calorie barcode scanner

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch — `git checkout -b feature/AmazingFeature`
3. Commit your changes — `git commit -m 'Add AmazingFeature'`
4. Push to the branch — `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👩‍💻 Author

**Vaishnavi Borusumedi**

[![GitHub](https://img.shields.io/badge/GitHub-vaishnaviborusumedi-black?style=flat-square&logo=github)](https://github.com/vaishnaviborusumedi)

---

## 🙏 Acknowledgements

- [USDA FoodData Central](https://fdc.nal.usda.gov/) — Nutrition data reference
- [OpenFoodFacts](https://world.openfoodfacts.org/) — Open source food database
- [Anthropic Claude](https://anthropic.com) — LLM for natural language recommendations
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework
- [Streamlit](https://streamlit.io) — Python frontend framework
- [mlxtend](http://rasbt.github.io/mlxtend/) — Apriori association rule mining
- [scikit-learn](https://scikit-learn.org) — K-Means clustering

---

<div align="center">
    <strong>Built with ❤️ and 🍛 by Vaishnavi Borusumedi</strong>
</div>
