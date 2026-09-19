from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models
from .database import get_db


app = FastAPI(
    title="Solvigo AI Case API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Solvigo API is running"
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }

@app.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(models.Brand).all()

    return brands

@app.get("/users/{user_id}/brands")
def get_user_brands(
    user_id: str,
    db: Session = Depends(get_db),
):

    user = (
        db.query(models.User)
        .filter(models.User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    
    brands = (
        db.query(models.Brand)
        .join(
            models.UserBrandAccess,
            models.Brand.brand_id == models.UserBrandAccess.brand_id,
        )
        .filter(models.UserBrandAccess.user_id == user_id)
        .all()
    )

    return brands