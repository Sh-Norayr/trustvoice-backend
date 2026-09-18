# TrustVoice AI — Backend (FastAPI)

This is the real backend behind the TrustVoice AI frontend prototype. It handles
account registration, login, sessions, and voice profile storage in an actual
database.

## What's real vs. what's still placeholder

✅ Real: user accounts, password hashing, JWT login, database storage, voice
profile settings, session records.

⚠️ Placeholder: when you "stop" a session, the confidence/clarity/stability/pace
numbers you get back are **randomly generated within realistic ranges** — not
computed from real audio. The real audio pipeline (speech-to-text, filler-word
detection, etc. — Phase 2 in the product spec) is not built yet. Every API
response that includes these numbers also includes a `notice` field saying so,
so nothing pretends to be more finished than it is.

## 1. Install Python dependencies

You need Python 3.10+ installed. Then, from this folder:

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Set up your environment file

```bash
cp .env.example .env
```

Open `.env` and change `SECRET_KEY` to something random (you can generate one
with `openssl rand -hex 32`). You can leave `DATABASE_URL` commented out —
that means it'll use a local SQLite file (`trustvoice.db`) with zero setup.

## 3. Run the server

```bash
uvicorn app.main:app --reload
```

You should see it running at **http://localhost:8000**.

## 4. Try it

Open **http://localhost:8000/docs** in your browser — FastAPI automatically
generates an interactive API playground (Swagger UI) where you can try every
endpoint (register, login, start a session, etc.) directly, no frontend needed.

## 5. Connect it to the frontend

The HTML frontend pages you already have (`trustvoice-signup.html`,
`trustvoice-login.html`, etc.) currently simulate signup/login with a fake
delay and no real network call. To connect them for real, each form's submit
handler needs to `fetch()` these endpoints instead, for example:

```js
const res = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, email, password })
});
const data = await res.json();
// data.access_token — save this (e.g. in memory or a cookie) and send it as
// "Authorization: Bearer <token>" on subsequent requests.
```

I can wire this up for you next — just ask.

## Switching to PostgreSQL later

When you're ready (per the original product spec), set `DATABASE_URL` in
`.env` to a real Postgres connection string, uncomment `psycopg2-binary` in
`requirements.txt`, reinstall, and restart the server. No code changes needed.

## Endpoints in this version

- `POST /api/auth/register` — create an account
- `POST /api/auth/login` — log in, get a token
- `GET /api/auth/me` — get the logged-in user's profile
- `GET /api/voice-profile` — get your voice profile
- `POST /api/voice-profile` — update your voice profile
- `POST /api/sessions/start` — start a session
- `POST /api/sessions/{id}/stop` — stop a session (generates placeholder metrics)
- `GET /api/sessions` — list your sessions
- `GET /api/sessions/{id}` — get one session's full detail
- `GET /api/sessions/{id}/analysis` — get just the AI coach analysis

All endpoints except register/login require an `Authorization: Bearer <token>`
header.
