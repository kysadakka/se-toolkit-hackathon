from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# User-Family many-to-many association table
user_family_assoc = Table(
    "user_families", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("family_id", Integer, ForeignKey("families.id"), primary_key=True),
)

class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", foreign_keys=[owner_id], backref="owned_families")
    items = relationship("Item", back_populates="family", cascade="all, delete-orphan")
    lists = relationship("ShoppingList", back_populates="family", cascade="all, delete-orphan")
    members = relationship("User", secondary=user_family_assoc, backref="families")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    active_family_id = Column(Integer, ForeignKey("families.id"), nullable=True)

    active_family = relationship("Family", foreign_keys=[active_family_id])

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    family_id = Column(Integer, ForeignKey("families.id"))

    family = relationship("Family", back_populates="lists")
    items = relationship("Item", back_populates="shopping_list", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quantity = Column(String, default="1")
    purchased = Column(Boolean, default=False)
    category = Column(String, default="Other")
    added_at = Column(DateTime, default=datetime.utcnow)
    family_id = Column(Integer, ForeignKey("families.id"))
    list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=True)

    family = relationship("Family", back_populates="items")
    shopping_list = relationship("ShoppingList", back_populates="items")
