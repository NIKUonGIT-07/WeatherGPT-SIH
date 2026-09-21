from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.auth_service import hash_password, verify_password
from app.services.jwt_service import create_access_token
from app.schemas.auth import UserCreate, UserResponse, UserLogin
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse
from app.services.auth_service import hash_password
from app.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if user.phone:
        existing_phone = (
            db.query(User)
            .filter(User.phone == user.phone)
            .first()
        )

        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Phone number already registered"
            )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = (
        db.query(User)
        .filter(
            (User.email == user.identifier) |
            (User.phone == user.identifier)
        )
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email/phone or password"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email/phone or password"
        )

    access_token = create_access_token({
        "user_id": existing_user.id,
        "email": existing_user.email
    })

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user