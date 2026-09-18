from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/voice-profile", tags=["voice-profile"])


@router.get("", response_model=schemas.VoiceProfileOut)
def get_voice_profile(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    profile = _get_or_create(db, current_user.id)
    return profile


@router.post("", response_model=schemas.VoiceProfileOut)
def update_voice_profile(
    payload: schemas.VoiceProfileIn,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    profile = _get_or_create(db, current_user.id)
    profile.preset = payload.preset
    profile.preferred_loudness = payload.preferred_loudness
    profile.preferred_pace = payload.preferred_pace
    profile.preferred_clarity = payload.preferred_clarity
    profile.processing_intensity = payload.processing_intensity
    db.commit()
    db.refresh(profile)
    return profile


def _get_or_create(db: DBSession, user_id: str) -> models.VoiceProfile:
    profile = db.query(models.VoiceProfile).filter(models.VoiceProfile.user_id == user_id).first()
    if not profile:
        profile = models.VoiceProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
