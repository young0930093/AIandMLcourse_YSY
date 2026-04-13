import os
import hmac
import hashlib
import json
import httpx
import aiosqlite
from fastapi import APIRouter, Header, HTTPException, Request, Depends
from datetime import datetime, timedelta
from auth import decode_token
from database import get_db

router = APIRouter(tags=["payment"])

POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN")
POLAR_PRODUCT_ID = os.getenv("POLAR_PRODUCT_ID")
POLAR_WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

POLAR_API_BASE = "https://sandbox-api.polar.sh"


@router.post("/api/subscribe/create")
async def create_checkout(
    authorization: str = Header(...),
    db: aiosqlite.Connection = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = await db.execute("SELECT email FROM users WHERE id=?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{POLAR_API_BASE}/v1/checkouts",
            headers={
                "Authorization": f"Bearer {POLAR_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "product_id": POLAR_PRODUCT_ID,
                "success_url": f"{FRONTEND_URL}/subscribe/success",
                "customer_email": user["email"],
                "metadata": {"user_id": str(user_id)},
            }
        )

    if resp.status_code != 201:
        raise HTTPException(status_code=502, detail="polar.sh checkout 생성 실패")

    data = resp.json()
    return {"checkout_url": data["url"]}


@router.post("/webhooks/polar")
async def polar_webhook(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db)
):
    body = await request.body()
    signature = request.headers.get("webhook-signature", "")

    if POLAR_WEBHOOK_SECRET:
        expected = hmac.new(
            POLAR_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = json.loads(body)
    event_type = payload.get("type")

    if event_type == "subscription.created":
        subscription_data = payload.get("data", {})
        user_id = subscription_data.get("metadata", {}).get("user_id")
        polar_sub_id = subscription_data.get("id")

        if user_id:
            expires_at = datetime.utcnow() + timedelta(days=30)
            await db.execute(
                """INSERT INTO subscriptions (user_id, polar_subscription_id, status, expires_at)
                   VALUES (?, ?, 'active', ?)""",
                (int(user_id), polar_sub_id, expires_at)
            )
            await db.commit()

    elif event_type == "subscription.cancelled":
        subscription_data = payload.get("data", {})
        polar_sub_id = subscription_data.get("id")
        await db.execute(
            "UPDATE subscriptions SET status='cancelled' WHERE polar_subscription_id=?",
            (polar_sub_id,)
        )
        await db.commit()

    return {"status": "ok"}
