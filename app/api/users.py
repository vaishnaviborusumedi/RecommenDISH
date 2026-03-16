from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.api.schemas import UserCreate, UserResponse
from app.ml.clustering import predict_cluster
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign cluster immediately
    try:
        user.cluster_id = predict_cluster(user, db)
        db.commit()
        db.refresh(user)
    except Exception as e:
        logger.warning(f"Clustering skipped: {e}")

    logger.info(f"Created user: {user.name} (id={user.id})")
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()