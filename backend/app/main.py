import os
import re
import json
import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from .database import SessionLocal
from . import models, schemas, auth, crud

app = FastAPI(title="Family Shopping List API")

QWEN_API_URL = os.getenv("QWEN_API_URL", "https://openrouter.ai/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    from .database import engine, Base
    Base.metadata.create_all(bind=engine)

# ---------- Dependency: get DB session ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Dependency: get current user from JWT ----------
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    email = auth.decode_access_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = auth.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ---------- AI Suggestions ----------
async def get_ai_suggestions(item_name: str) -> List[str]:
    """Call OpenRouter API to get related grocery item suggestions."""
    api_key = os.getenv("QWEN_API_KEY", "")
    if not api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{QWEN_API_URL}/chat/completions",
                json={
                    "model": "qwen/qwen-2.5-7b-instruct",
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                f"Suggest 3 related grocery items for '{item_name}'. "
                                "Return only a JSON object with this exact format: "
                                '{{"suggestions": ["item1", "item2", "item3"]}}. '
                                "No extra text."
                            )
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "http://localhost:42002",
                    "X-Title": "Family Shopping List",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                # Strip markdown code blocks if present
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                result = json.loads(content)
                return result.get("suggestions", [])
    except Exception:
        pass
    return []

# ---------- Auth Routes ----------
@app.post("/api/auth/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = auth.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = auth.create_user(db, user_data.email, user_data.password)
    return {"message": "User created"}

@app.post("/api/auth/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.email})
    families = crud.get_user_families(db, user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "active_family_id": user.active_family_id,
            "families": families,
        }
    }

@app.get("/api/auth/me", response_model=schemas.UserOut)
def get_me(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    families = crud.get_user_families(db, user.id)
    return {
        "id": user.id,
        "email": user.email,
        "active_family_id": user.active_family_id,
        "families": families,
    }

# ---------- Family Routes ----------
@app.post("/api/families")
def create_family(
    fam_data: schemas.FamilyCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = crud.create_family(db, fam_data.name, user.id, fam_data.password)
    user = db.query(models.User).filter(models.User.id == user.id).first()
    families = crud.get_user_families(db, user.id)
    return {
        "id": family.id,
        "name": family.name,
        "owner_id": family.owner_id,
        "created_at": family.created_at,
        "user": {
            "id": user.id,
            "email": user.email,
            "active_family_id": user.active_family_id,
            "families": families,
        }
    }

@app.post("/api/families/join")
def join_family(
    fam_data: schemas.FamilyJoin,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.join_family(db, user.id, fam_data.family_name, fam_data.password)
    if result is None:
        raise HTTPException(status_code=404, detail="Family not found")
    if result == "wrong_password":
        raise HTTPException(status_code=401, detail="Wrong password")
    if result == "already_member":
        raise HTTPException(status_code=400, detail="Already a member")
    user = db.query(models.User).filter(models.User.id == user.id).first()
    families = crud.get_user_families(db, user.id)
    return {
        "id": result.id,
        "name": result.name,
        "owner_id": result.owner_id,
        "created_at": result.created_at,
        "user": {
            "id": user.id,
            "email": user.email,
            "active_family_id": user.active_family_id,
            "families": families,
        }
    }

@app.post("/api/families/{family_id}/set-active")
def set_active_family(
    family_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = crud.set_active_family(db, user.id, family_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot switch to this family")
    return {"message": "Active family updated"}

@app.delete("/api/families/{family_id}/leave")
def leave_family(
    family_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success, message = crud.leave_family(db, user.id, family_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.delete("/api/families/{family_id}")
def delete_family(
    family_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success, message = crud.delete_family(db, user.id, family_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

# ---------- Shopping List Routes ----------
@app.get("/api/lists", response_model=List[schemas.ShoppingListOut])
def get_lists(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    return crud.get_lists(db, user.active_family_id)

@app.post("/api/lists", response_model=schemas.ShoppingListOut)
def create_list(
    list_data: schemas.ShoppingListCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    return crud.create_list(db, list_data, user.active_family_id)

@app.delete("/api/lists/{list_id}")
def delete_list(
    list_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    success = crud.delete_list(db, list_id, user.active_family_id)
    if not success:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted"}

# ---------- Item Routes ----------
@app.get("/api/items", response_model=List[schemas.ItemOut])
def get_items(
    list_id: Optional[int] = None,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    return crud.get_items(db, user.active_family_id, list_id)

@app.post("/api/items", response_model=schemas.ItemOut)
async def create_item(
    item_data: schemas.ItemCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    created_item = crud.create_item(db, item_data, user.active_family_id)
    suggestions = await get_ai_suggestions(item_data.name)
    result = schemas.ItemOut(
        id=created_item.id,
        name=created_item.name,
        quantity=created_item.quantity,
        purchased=created_item.purchased,
        category=created_item.category,
        list_id=created_item.list_id,
        suggestions=suggestions,
    )
    return result

@app.patch("/api/items/{item_id}", response_model=schemas.ItemOut)
def toggle_item_purchased(
    item_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    item = crud.toggle_item_purchased(db, item_id, user.active_family_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/api/items/{item_id}")
def delete_item(
    item_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    success = crud.delete_item(db, item_id, user.active_family_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# ---------- History Routes ----------
@app.get("/api/history", response_model=List[schemas.HistoryItem])
def get_history(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.active_family_id:
        raise HTTPException(status_code=400, detail="No active family")
    return crud.get_history(db, user.active_family_id)
