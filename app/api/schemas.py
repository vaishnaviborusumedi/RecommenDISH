from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    weight_kg: float
    height_cm: float
    sex: str
    activity_level: int
    goal: str
    allergies: Optional[str] = ""
    conditions: Optional[str] = ""


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    weight_kg: float
    height_cm: float
    sex: str
    activity_level: int
    goal: str
    allergies: Optional[str]
    cluster_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MealLogCreate(BaseModel):
    food_id: int
    meal_type: str
    portion_g: float
    rating: Optional[int] = None


class MealLogResponse(BaseModel):
    id: int
    user_id: int
    food_id: int
    meal_type: str
    portion_g: float
    rating: Optional[int]
    logged_at: datetime

    class Config:
        from_attributes = True


class FoodResponse(BaseModel):
    id: int
    name: str
    category: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool

    class Config:
        from_attributes = True


class RecommendationItem(BaseModel):
    food_id: int
    food_name: str
    category: str
    calories: float
    protein_g: float
    fiber_g: float
    score: float
    rule_match: bool
    peer_match: bool


class RecommendationResponse(BaseModel):
    user_name: str
    goal: str
    gaps: dict
    recommendations: list[RecommendationItem]
    llm_suggestion: str