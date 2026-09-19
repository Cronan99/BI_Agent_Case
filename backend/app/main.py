from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from . import models
from .database import get_db
from .services.sales_service import get_sales_summary
from .services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user
)
from .agent.agent import ask_agent


app = FastAPI(
    title="Solvigo AI Case API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str


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

@app.get("/sales/summary")
def sales_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    city: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    return get_sales_summary(
        db=db,
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
        region=region,
        city=city,
    )

@app.post("/auth/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user_id=user.user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/auth/me")
def get_me(
    current_user: models.User = Depends(get_current_user),
):
    return {
        "user_id": current_user.user_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "company": current_user.company,
        "role": current_user.role,
        "brands": [
            {
                "brand_id": access.brand.brand_id,
                "brand_name": access.brand.brand_name,
            }
            for access in current_user.brand_access
        ]
    }

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    answer = ask_agent(
        message=request.message,
        db=db,
        current_user=current_user,
    )

    return {"answer": answer}