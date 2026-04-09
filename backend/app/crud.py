from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .auth import get_password_hash

# ---------- Family Management ----------
def get_user_families(db: Session, user_id: int):
    """Get all families the user belongs to, with role info."""
    families = db.query(models.Family).join(
        models.user_family_assoc,
        models.Family.id == models.user_family_assoc.c.family_id
    ).filter(
        models.user_family_assoc.c.user_id == user_id
    ).all()

    result = []
    for f in families:
        member_count = db.query(func.count(models.user_family_assoc.c.user_id)).filter(
            models.user_family_assoc.c.family_id == f.id
        ).scalar()
        result.append({
            "id": f.id,
            "name": f.name,
            "is_owner": f.owner_id == user_id,
            "member_count": member_count
        })
    return result

def create_family(db: Session, name: str, user_id: int, password: str):
    """Create a new family with user as owner and first member."""
    family = models.Family(name=name, owner_id=user_id, hashed_password=get_password_hash(password))
    db.add(family)
    db.flush()
    # Add owner as member
    user = db.query(models.User).filter(models.User.id == user_id).first()
    family.members.append(user)
    # Set as user's active family
    user.active_family_id = family.id
    db.commit()
    db.refresh(family)
    return family

def join_family(db: Session, user_id: int, family_name: str, password: str):
    """Add user to an existing family with password verification."""
    family = db.query(models.Family).filter(models.Family.name.ilike(family_name)).first()
    if not family:
        return None
    # Verify password
    from .auth import verify_password
    if not verify_password(password, family.hashed_password):
        return "wrong_password"
    user = db.query(models.User).filter(models.User.id == user_id).first()
    # Check if already a member
    if user in family.members:
        return "already_member"
    family.members.append(user)
    # Set as user's active family
    user.active_family_id = family.id
    db.commit()
    db.refresh(family)
    return family

def leave_family(db: Session, user_id: int, family_id: int):
    """Remove user from a family. Owner cannot leave own family."""
    family = db.query(models.Family).filter(models.Family.id == family_id).first()
    if not family:
        return False, "Family not found"
    if family.owner_id == user_id:
        return False, "Owner cannot leave family. Delete the family instead."
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user not in family.members:
        return False, "Not a member"
    family.members.remove(user)
    # If this was the user's active family, clear it
    if user.active_family_id == family_id:
        user.active_family_id = None
    db.commit()
    return True, "Left family"

def delete_family(db: Session, user_id: int, family_id: int):
    """Delete a family. Only owner can delete. Cascades to items/lists."""
    family = db.query(models.Family).filter(models.Family.id == family_id).first()
    if not family:
        return False, "Family not found"
    if family.owner_id != user_id:
        return False, "Only owner can delete family"
    # Clear active_family_id for ALL members who have this as active
    members = db.query(models.User).filter(
        models.User.active_family_id == family_id
    ).all()
    for member in members:
        member.active_family_id = None
    db.flush()
    db.delete(family)
    db.commit()
    return True, "Family deleted"

def set_active_family(db: Session, user_id: int, family_id: int):
    """Set the user's active family."""
    family = db.query(models.Family).filter(models.Family.id == family_id).first()
    if not family:
        return False
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user not in family.members:
        return False
    user.active_family_id = family_id
    db.commit()
    return True

# ---------- Shopping Lists ----------
def get_lists(db: Session, family_id: int):
    return db.query(models.ShoppingList).filter(models.ShoppingList.family_id == family_id).all()

def create_list(db: Session, list_data: schemas.ShoppingListCreate, family_id: int):
    db_list = models.ShoppingList(name=list_data.name, family_id=family_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def delete_list(db: Session, list_id: int, family_id: int):
    shopping_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        models.ShoppingList.family_id == family_id
    ).first()
    if shopping_list:
        db.delete(shopping_list)
        db.commit()
        return True
    return False

# ---------- Items ----------
def get_items(db: Session, family_id: int, list_id: int | None = None):
    query = db.query(models.Item).filter(
        models.Item.family_id == family_id,
        models.Item.purchased == False
    )
    if list_id is not None:
        query = query.filter(models.Item.list_id == list_id)
    return query.all()

def create_item(db: Session, item: schemas.ItemCreate, family_id: int):
    db_item = models.Item(
        name=item.name,
        quantity=item.quantity,
        family_id=family_id,
        list_id=item.list_id,
        category=item.category
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def toggle_item_purchased(db: Session, item_id: int, family_id: int):
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.family_id == family_id
    ).first()
    if item:
        item.purchased = not item.purchased
        db.commit()
        db.refresh(item)
    return item

def delete_item(db: Session, item_id: int, family_id: int):
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.family_id == family_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

# ---------- Purchase History ----------
def get_history(db: Session, family_id: int, limit: int = 50):
    return db.query(models.Item).filter(
        models.Item.family_id == family_id,
        models.Item.purchased == True
    ).order_by(models.Item.added_at.desc()).limit(limit).all()
