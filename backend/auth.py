import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
import aiosqlite
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        return None


@router.get("/google")
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(code: str, db: aiosqlite.Connection = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo = userinfo_resp.json()

    google_id = userinfo["sub"]
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")
    picture = userinfo.get("picture", "")

    cursor = await db.execute(
        "SELECT id FROM users WHERE google_id = ?", (google_id,)
    )
    row = await cursor.fetchone()

    if row:
        user_id = row["id"]
        await db.execute(
            "UPDATE users SET name=?, picture=? WHERE id=?",
            (name, picture, user_id)
        )
    else:
        cursor = await db.execute(
            "INSERT INTO users (google_id, email, name, picture) VALUES (?,?,?,?)",
            (google_id, email, name, picture)
        )
        user_id = cursor.lastrowid

    await db.commit()
    jwt_token = create_access_token(user_id)
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={jwt_token}")


@router.get("/me")
async def get_me(token: str, db: aiosqlite.Connection = Depends(get_db)):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sub_cursor = await db.execute(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    subscription = await sub_cursor.fetchone()

    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
        "is_subscribed": subscription is not None,
    }
