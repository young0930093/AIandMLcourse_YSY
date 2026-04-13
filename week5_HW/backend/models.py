from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]
    picture: Optional[str]
    is_subscribed: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CoursePreview(BaseModel):
    id: int
    title: str
    description: str
    is_free: bool
    duration: str
    level: str

class CourseDetail(BaseModel):
    id: int
    title: str
    description: str
    is_free: bool
    duration: str
    level: str
    content: Optional[dict] = None

class CheckoutResponse(BaseModel):
    checkout_url: str

class SubscriptionStatus(BaseModel):
    is_subscribed: bool
    expires_at: Optional[datetime] = None
