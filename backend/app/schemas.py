from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ---------- Auth ----------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class FamilyInfo(BaseModel):
    id: int
    name: str
    is_owner: bool
    member_count: int

class UserOut(BaseModel):
    id: int
    email: str
    active_family_id: Optional[int] = None
    families: List[FamilyInfo] = []

# ---------- Family Management ----------
class FamilyCreate(BaseModel):
    name: str
    password: str

class FamilyJoin(BaseModel):
    family_name: str
    password: str

class FamilyOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Shopping Lists ----------
class ShoppingListCreate(BaseModel):
    name: str

class ShoppingListOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Items ----------
class ItemCreate(BaseModel):
    name: str
    quantity: str = "1"
    list_id: Optional[int] = None
    category: str = "Other"

class ItemOut(BaseModel):
    id: int
    name: str
    quantity: str
    purchased: bool
    category: str
    list_id: Optional[int] = None
    suggestions: List[str] = []

    class Config:
        from_attributes = True

# ---------- History ----------
class HistoryItem(BaseModel):
    id: int
    name: str
    quantity: str
    purchased: bool
    category: str
    added_at: datetime
