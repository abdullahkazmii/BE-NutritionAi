import string
import secrets
from typing import List
from app.models import User
from app import models, schemas
from app.database import get_db
from sqlalchemy.orm import Session
from app.auth.utils import hash_password
from app.auth.oauth import admin_required
from fastapi import Response, status, HTTPException, Depends, APIRouter

router = APIRouter(tags=["User"])


@router.get(
    "/users", response_model=List[schemas.UserOut], status_code=status.HTTP_200_OK
)
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    users = db.query(models.User).all()
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
        )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can get users"
        )
    return users


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponseWithPassword,
)
def create_user(
    user: schemas.CreateUser,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    alphabet = string.ascii_letters + string.digits
    generated_password = "".join(secrets.choice(alphabet) for _ in range(8))
    hashed_password = hash_password(generated_password)
    user_data = user.model_dump(exclude={"password"})
    new_user = models.User(**user_data, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user": new_user, "password": generated_password}


@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    user_to_delete = db.query(models.User).filter(models.User.id == id).first()
    if user_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id '{id}' not found",
        )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete users"
        )

    if user_to_delete.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot delete other admins",
        )

    db.query(models.User).filter(models.User.id == id).delete(synchronize_session=False)
    db.commit()
    return Response(
        f"User with id {id} has been deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.patch(
    "/user/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserResponseWithPassword,
)
def update_user(
    id: int,
    user: schemas.UpdateUser,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    existing_user = db.query(models.User).filter(models.User.id == id).first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id '{id}' not found",
        )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update users",
        )
    if existing_user.role == "admin" and existing_user.id != admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot edit other admins",
        )

    if user.name is not None:
        existing_user.name = user.name
    if user.email is not None:
        existing_user.email = user.email
    if user.username is not None:
        existing_user.username = user.username
    if user.role is not None:
        existing_user.role = user.role

    password_to_return = None
    if user.password:
        existing_user.password = hash_password(user.password)
        password_to_return = user.password

    db.commit()
    db.refresh(existing_user)

    return {"user": existing_user, "password": password_to_return}
