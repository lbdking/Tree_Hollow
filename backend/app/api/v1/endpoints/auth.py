from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut, UserUpdateIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if crud.user.user.get_by_student_id(db, payload.student_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "该学号已注册")
    u = crud.user.user.create(
        db,
        obj_in={
            "student_id": payload.student_id,
            "password_hash": hash_password(payload.password),
            "real_name": payload.real_name,
            "role": "student",
        },
    )
    token = create_access_token(str(u.id), u.role)
    return TokenOut(access_token=token, user=UserOut.model_validate(u))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = crud.user.user.get_by_student_id(db, payload.student_id)
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "学号或密码错误")
    token = create_access_token(str(u.id), u.role)
    return TokenOut(access_token=token, user=UserOut.model_validate(u))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    u = crud.user.user.update(db, db_obj=user, obj_in=payload.model_dump(exclude_unset=True))
    return UserOut.model_validate(u)
