from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import MealLog, User, Food
from app.api.schemas import MealLogCreate, MealLogResponse
from app.utils.logger import logger

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/{user_id}", response_model=MealLogResponse)
def log_meal(user_id: int, payload: MealLogCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    food = db.query(Food).filter(Food.id == payload.food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    log = MealLog(user_id=user_id, **payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)

    logger.info(f"User {user_id} logged {food.name} ({payload.portion_g}g)")
    return log


@router.get("/{user_id}", response_model=list[MealLogResponse])
def get_meal_logs(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logs = db.query(MealLog).filter(MealLog.user_id == user_id).all()
    return logs