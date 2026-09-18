from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from . import models
from .database import engine
from .limiter import limiter
from .routers import auth as auth_router
from .routers import sessions as sessions_router
from .routers import voice_profile as voice_profile_router

# Creates tables on first run. For real schema changes later, switch to Alembic migrations.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrustVoice AI API", version="0.1.0")

# --- Rate limiting (protects auth endpoints from brute force / abuse) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS: allow the frontend dev server to call this API ---
# Tighten allow_origins to your real frontend domain(s) before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(sessions_router.router)
app.include_router(voice_profile_router.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "TrustVoice AI API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def friendly_error_handler(request: Request, exc: Exception):
    # Never leak raw internal errors to the client (spec: friendly error messages only).
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )
