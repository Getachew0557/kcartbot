"""Database models for KcartBot."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for customers and suppliers."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    user_type = Column(String(20), nullable=False)  # 'customer' or 'supplier'
    default_location = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    """Product model."""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    name_amharic = Column(String(200))  # Amharic name
    category = Column(String(50), nullable=False)  # 'horticulture' or 'dairy'
    unit = Column(String(20), default="kg")  # kg or liter
    description = Column(Text)
    supplier_id = Column(String, ForeignKey("users.id"))
    current_price = Column(Float, nullable=False)
    quantity_available = Column(Float, default=0)
    expiry_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    supplier = relationship("User", back_populates="products")
    orders = relationship("Order", back_populates="product")
    pricing_history = relationship("PricingHistory", back_populates="product")


class Order(Base):
    """Order model."""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    product_id = Column(String, ForeignKey("products.id"))
    quantity_ordered = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    delivery_date = Column(DateTime)
    delivery_location = Column(String(200))
    payment_method = Column(String(20), default="COD")
    status = Column(String(20), default="pending")  # pending, confirmed, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


class PricingHistory(Base):
    """Historical pricing data."""
    __tablename__ = "pricing_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"))
    price = Column(Float, nullable=False)
    source_market_type = Column(String(50))  # 'local_shop', 'supermarket', 'distribution_center'
    location_detail = Column(String(200))
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="pricing_history")


class ProductKnowledge(Base):
    """Product knowledge base for RAG."""
    __tablename__ = "product_knowledge"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"))
    knowledge_type = Column(String(50))  # 'storage', 'nutrition', 'recipe', 'seasonal'
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product")


class ChatSession(Base):
    """Chat session tracking."""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    session_data = Column(Text)  # JSON string for session state
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

