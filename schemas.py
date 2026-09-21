from pydantic import BaseModel, HttpUrl
from datetime import datetime, timezone, timedelta
from typing import Optional

class URLBase(BaseModel):
    original_url: HttpUrl

class UserBase(BaseModel):
    username: str
    email: str



class URLCreate(URLBase):
    custom_code: Optional[str] = None
    expires_in_minutes: Optional[int] = None

class URLResponse(URLBase):
    id: int
    short_url: str
    clicks: int
    created_at: datetime
    owner_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_expired: bool

    model_config = {
        "from_attributes": True
    }


class UserCreate(UserBase):
    username: str
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TokenData(BaseModel):
    username: Optional[str] = None