# auth.py — FinMate AI Authentication System
# pip install python-jose[cryptography] python-multipart bcrypt

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3, os, json, bcrypt as _bcrypt, hashlib, base64

# ─── Config ──────────────────────────────────────────────────────
SECRET_KEY               = os.getenv("JWT_SECRET", "finmate-super-secret-key-change-in-production-2024")
ALGORITHM                = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
DB_FILE                  = "finmate.db"

bearer = HTTPBearer(auto_error=False)

# ─── Database Setup ───────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c    = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now')),
            last_login    TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id      INTEGER PRIMARY KEY,
            salary       INTEGER DEFAULT 0,
            expenses     INTEGER DEFAULT 0,
            goals        TEXT    DEFAULT '[]',
            risk_profile TEXT    DEFAULT 'moderate',
            conversation TEXT    DEFAULT '[]',
            watchlist    TEXT    DEFAULT '[]',
            updated_at   TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()
    print("✓ Database initialized — finmate.db")

# ─── Password Utils ───────────────────────────────────────────────
# SHA256 first → bcrypt (fixes 72-byte limit + passlib version issues)
def _prepare(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(_prepare(password), _bcrypt.gensalt(12)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(_prepare(plain), hashed.encode("utf-8"))
    except Exception:
        return False

# ─── JWT Utils ────────────────────────────────────────────────────
def create_token(user_id: int, email: str, name: str) -> str:
    expire  = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub"  : str(user_id),
        "email": email,
        "name" : name,
        "exp"  : expire,
        "iat"  : datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# ─── Auth Dependency ──────────────────────────────────────────────
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "user_id": int(payload["sub"]),
        "email"  : payload["email"],
        "name"   : payload["name"],
    }

def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    return {
        "user_id": int(payload["sub"]),
        "email"  : payload["email"],
        "name"   : payload["name"],
    }

# ─── Profile DB helpers ───────────────────────────────────────────
def load_user_profile(user_id: int) -> dict:
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {
            "user_id": user_id, "salary": 0, "expenses": 0,
            "goals": [], "risk_profile": "moderate",
            "conversation": [], "watchlist": []
        }
    return {
        "user_id"     : user_id,
        "salary"      : row["salary"],
        "expenses"    : row["expenses"],
        "goals"       : json.loads(row["goals"]        or "[]"),
        "risk_profile": row["risk_profile"]             or "moderate",
        "conversation": json.loads(row["conversation"] or "[]"),
        "watchlist"   : json.loads(row["watchlist"]    or "[]"),
    }

def save_user_profile(user_id: int, profile: dict):
    conn = get_db()
    conn.execute("""
        INSERT INTO user_profiles
            (user_id, salary, expenses, goals, risk_profile, conversation, watchlist, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            salary       = excluded.salary,
            expenses     = excluded.expenses,
            goals        = excluded.goals,
            risk_profile = excluded.risk_profile,
            conversation = excluded.conversation,
            watchlist    = excluded.watchlist,
            updated_at   = excluded.updated_at
    """, (
        user_id,
        profile.get("salary",   0),
        profile.get("expenses", 0),
        json.dumps(profile.get("goals",        [])),
        profile.get("risk_profile", "moderate"),
        json.dumps(profile.get("conversation", [])[-30:]),
        json.dumps(profile.get("watchlist",    [])),
    ))
    conn.commit()
    conn.close()