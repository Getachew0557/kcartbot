from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

# SQLite compatible UUID type
class UUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            return str(value) if not isinstance(value, str) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        # Normalize all UUID-like return types (uuid.UUID, bytes, str) to str
        try:
            return str(value)
        except Exception:
            return value

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    location = Column(String(200))
    user_type = Column(String(20), default="customer")
    created_at = Column(DateTime, default=func.now())

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    unit = Column(String(20), default="kg")
    current_price = Column(Float)
    supplier_id = Column(UUID(), ForeignKey('suppliers.id'))
    expiry_date = Column(DateTime, nullable=True)
    stock_quantity = Column(Float, default=0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())

class ProductKnowledge(Base):
    __tablename__ = "product_knowledge"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(), ForeignKey('products.id'))
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    language = Column(String(10), default="english")

class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(), ForeignKey('products.id'))
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    source_market_type = Column(String(50))
    location_detail = Column(String(200))
    created_at = Column(DateTime, default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    order_date = Column(DateTime, nullable=False)
    user_id = Column(UUID(), ForeignKey('users.id'))
    user_name = Column(String(100))
    phone = Column(String(20))
    supplier_id = Column(UUID(), ForeignKey('suppliers.id'))
    product_id = Column(UUID(), ForeignKey('products.id'))
    product_name = Column(String(100))
    quantity_ordered = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    price_per_unit = Column(Float, nullable=False)
    order_total_amount = Column(Float, nullable=False)
    delivery_date = Column(DateTime)
    delivery_location = Column(String(200))
    status = Column(String(20), default="confirmed")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey('users.id'))
    supplier_id = Column(UUID(), ForeignKey('suppliers.id'))
    product_id = Column(UUID(), ForeignKey('products.id'))
    quantity = Column(Float, nullable=False)
    delivery_date = Column(DateTime)
    delivery_location = Column(String(200))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=func.now())