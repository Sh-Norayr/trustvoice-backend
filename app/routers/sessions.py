import random
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/start", response_model=schemas.SessionOut, status_code=201)
def start_session(
    payload: schemas.SessionCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = models.Session(user_id=current_user.id, title=payload.title or "Session")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/stop", response_model=schemas.SessionDetailOut)
def stop_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = _get_owned_session(db, session_id, current_user.id)
    if session.status != "active":
        raise HTTPException(status_code=400, detail="This session is already stopped.")

    session.ended_at = datetime.datetime.utcnow()
    session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    session.status = "completed"

    # --- PLACEHOLDER METRICS ---
    # There is no real audio pipeline wired in yet (see spec Phase 2: speech-to-text,
    # filler-word detection, confidence modeling). Until that exists, we generate
    # plausible, clearly-labeled placeholder metrics so the frontend has real data
    # to render against. Replace this block with a call into the analysis pipeline
    # once Phase 2 is implemented — do not present this as real analysis to users.
    metrics = models.SessionMetrics(
        session_id=session.id,
        confidence_score=round(random.uniform(68, 92), 1),
        clarity_score=round(random.uniform(75, 95), 1),
        stability_score=round(random.uniform(70, 94), 1),
        energy_score=round(random.uniform(60, 88), 1),
        speaking_wpm=round(random.uniform(120, 165), 1),
        filler_words_per_min=round(random.uniform(0.5, 3.0), 1),
        pause_count=random.randint(4, 22),
    )
    db.add(metrics)

    analysis = models.AIAnalysis(
        session_id=session.id,
        strengths="Your voice stayed relatively steady through most of the session.",
        improvements="Pace picked up in later portions of the conversation.",
        coach_note="Try pausing briefly before answering more complex questions.",
    )
    db.add(analysis)

    db.commit()
    db.refresh(session)

    result = schemas.SessionDetailOut.model_validate(session)
    result.notice = "Metrics are prototype placeholders. Real audio analysis (Phase 2) is not yet wired in."
    return result


@router.get("", response_model=list[schemas.SessionOut])
def list_sessions(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Session)
        .filter(models.Session.user_id == current_user.id)
        .order_by(models.Session.started_at.desc())
        .all()
    )


@router.get("/{session_id}", response_model=schemas.SessionDetailOut)
def get_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = _get_owned_session(db, session_id, current_user.id)
    result = schemas.SessionDetailOut.model_validate(session)
    if session.metrics:
        result.notice = "Metrics are prototype placeholders. Real audio analysis (Phase 2) is not yet wired in."
    return result


@router.get("/{session_id}/analysis", response_model=schemas.AIAnalysisOut)
def get_session_analysis(
    session_id: str,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = _get_owned_session(db, session_id, current_user.id)
    if not session.analysis:
        raise HTTPException(status_code=404, detail="No analysis available for this session yet.")
    return session.analysis


def _get_owned_session(db: DBSession, session_id: str, user_id: str) -> models.Session:
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have access to this session.")
    return session
