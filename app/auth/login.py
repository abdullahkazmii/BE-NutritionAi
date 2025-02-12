from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from datetime import timedelta
from app.auth.utils import verify_password
from app.auth.oauth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserOut
from app.auth.oauth import admin_required

router = APIRouter(tags=["Login"])


@router.post("/login/", status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role}, expires_delta=access_token_expires
    )

    return {
        "User": UserOut.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/admin/login/", status_code=status.HTTP_200_OK)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can log in here.",
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role}, expires_delta=access_token_expires
    )

    return {
        "User": UserOut.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer",
    }
