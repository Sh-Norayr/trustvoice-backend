from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session as DBSession

from .. import models, schemas, auth
from ..database import get_db
from ..limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: schemas.UserRegister, db: DBSession = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Give every new user a default voice profile so /api/voice-profile always has something to return.
    profile = models.VoiceProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    token = auth.create_access_token(user.id)
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.Token)
@limiter.limit("10/minute")
def login(request: Request, payload: schemas.UserLogin, db: DBSession = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    # Always run verify_password (even on a missing user, against a dummy hash) so that
    # response timing doesn't reveal whether an email exists in the system.
    dummy_hash = "$2b$12$CwdmL8/AaXajQ0F9AzUx6.06TZBRLK3F0F1J1p5xnI/A9r0lTPuv6"
    valid = auth.verify_password(payload.password, user.password_hash if user else dummy_hash)

    if not user or not valid:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = auth.create_access_token(user.id)
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
