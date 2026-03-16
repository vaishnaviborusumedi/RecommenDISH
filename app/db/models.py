from sqlalchemy import (
    Column, Integer, String, Float,
    Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    age = Column(Integer)
    weight_kg = Column(Float)
    height_cm = Column(Float)
    sex = Column(String(10))           # male / female / other
    activity_level = Column(Integer)   # 1 (sedentary) to 5 (very active)
    goal = Column(String(50))          # lose_weight / gain_muscle / maintain
    allergies = Column(Text)           # comma-separated e.g. "gluten,dairy"
    conditions = Column(Text)          # comma-separated e.g. "diabetes"
    cluster_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meals = relationship("MealLog", back_populates="user")


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100))     # grain, protein, vegetable, dairy, fruit, fat
    calories = Column(Float)           # per 100g
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    fiber_g = Column(Float)
    sugar_g = Column(Float)
    sodium_mg = Column(Float)
    vitamin_c_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)
    calcium_mg = Column(Float, nullable=True)
    glycemic_index = Column(Float, nullable=True)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)

    meal_logs = relationship("MealLog", back_populates="food")


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    meal_type = Column(String(20))     # breakfast / lunch / dinner / snack
    portion_g = Column(Float)          # grams consumed
    rating = Column(Integer, nullable=True)   # 1-5 user rating
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="meals")
    food = relationship("Food", back_populates="meal_logs")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    score = Column(Float)
    reason = Column(Text)              # LLM-generated explanation
    was_accepted = Column(Boolean, nullable=True)   # user feedback
    created_at = Column(DateTime(timezone=True), server_default=func.now())