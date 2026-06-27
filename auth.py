# auth.py — FinMate AI Authentication System
# PostgreSQL (production) + SQLite (local dev) dual mode

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os, json, bcrypt as _bcrypt, hashlib, base64

SECRET_KEY               = os.getenv("JWT_SECRET", "finmate-super-secret-key-2024")
ALGORITHM                = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
DATABASE_URL             = os.getenv("DATABASE_URL", "")
DB_FILE                  = "finmate.db"

bearer       = HTTPBearer(auto_error=False)
USE_POSTGRES = bool(DATABASE_URL and DATABASE_URL.startswith("postgresql"))

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    print("✓ Using PostgreSQL (Supabase)")
else:
    import sqlite3
    print("✓ Using SQLite (local dev)")

# ─── DB Connection ────────────────────────────────────────────────
def get_db():
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require",
                                cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

# ─── Placeholder for parameterized queries ────────────────────────
PH = "%s" if USE_POSTGRES else "?"

# ─── DB Init ──────────────────────────────────────────────────────
def init_db():
    conn = get_db()
    c    = conn.cursor()

    if USE_POSTGRES:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                name          TEXT      NOT NULL,
                email         TEXT      UNIQUE NOT NULL,
                password_hash TEXT      NOT NULL,
                created_at    TIMESTAMP DEFAULT NOW(),
                last_login    TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id       INTEGER   PRIMARY KEY REFERENCES users(id),
                salary        INTEGER   DEFAULT 0,
                expenses      INTEGER   DEFAULT 0,
                goals         TEXT      DEFAULT '[]',
                risk_profile  TEXT      DEFAULT 'moderate',
                trading_style TEXT      DEFAULT 'swing',
                conversation  TEXT      DEFAULT '[]',
                watchlist     TEXT      DEFAULT '[]',
                updated_at    TIMESTAMP DEFAULT NOW()
            )
        """)
        try:
            c.execute("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS trading_style TEXT DEFAULT 'swing'")
        except: pass
    else:
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
                user_id       INTEGER PRIMARY KEY,
                salary        INTEGER DEFAULT 0,
                expenses      INTEGER DEFAULT 0,
                goals         TEXT    DEFAULT '[]',
                risk_profile  TEXT    DEFAULT 'moderate',
                trading_style TEXT    DEFAULT 'swing',
                conversation  TEXT    DEFAULT '[]',
                watchlist     TEXT    DEFAULT '[]',
                updated_at    TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        try:
            c.execute("ALTER TABLE user_profiles ADD COLUMN trading_style TEXT DEFAULT 'swing'")
        except: pass

    conn.commit()
    conn.close()
    print("✓ Database initialized")

# ─── Password Utils ───────────────────────────────────────────────
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

# ─── DB query helper ──────────────────────────────────────────────
def fetchone(conn, query, params=()):
    """Execute query and return one row as dict."""
    c = conn.cursor()
    # Replace ? with %s for postgres
    if USE_POSTGRES:
        query = query.replace("?", "%s")
    c.execute(query, params)
    row = c.fetchone()
    if row is None:
        return None
    if USE_POSTGRES:
        return dict(row)  # RealDictCursor returns dict-like
    return dict(row)      # sqlite3.Row also supports dict()

def execute(conn, query, params=()):
    """Execute a write query."""
    c = conn.cursor()
    if USE_POSTGRES:
        query = query.replace("?", "%s")
    c.execute(query, params)
    # Return lastrowid for INSERT
    if USE_POSTGRES:
        try:
            return c.fetchone()  # For RETURNING clause
        except:
            return None
    return c.lastrowid

# ─── Profile Helpers ──────────────────────────────────────────────
def load_user_profile(user_id: int) -> dict:
    conn = get_db()
    try:
        row = fetchone(conn, "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    finally:
        conn.close()

    if not row:
        return {
            "user_id"      : user_id,
            "salary"       : 0,
            "expenses"     : 0,
            "goals"        : [],
            "risk_profile" : "moderate",
            "trading_style": "swing",
            "conversation" : [],
            "watchlist"    : [],
        }
    return {
        "user_id"      : user_id,
        "salary"       : row.get("salary", 0),
        "expenses"     : row.get("expenses", 0),
        "goals"        : json.loads(row.get("goals") or "[]"),
        "risk_profile" : row.get("risk_profile") or "moderate",
        "trading_style": row.get("trading_style") or "swing",
        "conversation" : json.loads(row.get("conversation") or "[]"),
        "watchlist"    : json.loads(row.get("watchlist") or "[]"),
    }

def save_user_profile(user_id: int, profile: dict):
    conn = get_db()
    try:
        goals  = json.dumps(profile.get("goals",        []))
        conv   = json.dumps(profile.get("conversation", [])[-30:])
        watchl = json.dumps(profile.get("watchlist",    []))

        if USE_POSTGRES:
            c = conn.cursor()
            c.execute("""
                INSERT INTO user_profiles
                    (user_id, salary, expenses, goals, risk_profile, trading_style, conversation, watchlist, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    salary        = EXCLUDED.salary,
                    expenses      = EXCLUDED.expenses,
                    goals         = EXCLUDED.goals,
                    risk_profile  = EXCLUDED.risk_profile,
                    trading_style = EXCLUDED.trading_style,
                    conversation  = EXCLUDED.conversation,
                    watchlist     = EXCLUDED.watchlist,
                    updated_at    = NOW()
            """, (
                user_id,
                profile.get("salary",        0),
                profile.get("expenses",      0),
                goals,
                profile.get("risk_profile",  "moderate"),
                profile.get("trading_style", "swing"),
                conv,
                watchl,
            ))
        else:
            c = conn.cursor()
            c.execute("""
                INSERT INTO user_profiles
                    (user_id, salary, expenses, goals, risk_profile, trading_style, conversation, watchlist, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    salary        = excluded.salary,
                    expenses      = excluded.expenses,
                    goals         = excluded.goals,
                    risk_profile  = excluded.risk_profile,
                    trading_style = excluded.trading_style,
                    conversation  = excluded.conversation,
                    watchlist     = excluded.watchlist,
                    updated_at    = excluded.updated_at
            """, (
                user_id,
                profile.get("salary",        0),
                profile.get("expenses",      0),
                goals,
                profile.get("risk_profile",  "moderate"),
                profile.get("trading_style", "swing"),
                conv,
                watchl,
            ))
        conn.commit()
    finally:
        conn.close()