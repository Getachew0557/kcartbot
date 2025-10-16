"""Data generation script for KcartBot synthetic dataset."""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
from sqlalchemy.orm import Session

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.connection import SessionLocal, init_database
from src.models import User, Product, Order, PricingHistory, ProductKnowledge

fake = Faker()

# Ethiopian horticulture and dairy products
PRODUCTS_DATA = [
    # Horticulture products
    {"name": "Red Onion", "name_amharic": "ሃበሻ", "category": "horticulture", "unit": "kg"},
    {"name": "Tomato", "name_amharic": "ቲማቲም", "category": "horticulture", "unit": "kg"},
    {"name": "Potato", "name_amharic": "ድንች", "category": "horticulture", "unit": "kg"},
    {"name": "Avocado", "name_amharic": "አቮካዶ", "category": "horticulture", "unit": "kg"},
    {"name": "Banana", "name_amharic": "ሙዝ", "category": "horticulture", "unit": "kg"},
    {"name": "Mango", "name_amharic": "ማንጎ", "category": "horticulture", "unit": "kg"},
    {"name": "Papaya", "name_amharic": "ፓፓያ", "category": "horticulture", "unit": "kg"},
    {"name": "White Cabbage", "name_amharic": "ጠቅላላ", "category": "horticulture", "unit": "kg"},
    {"name": "Carrot", "name_amharic": "ካሮት", "category": "horticulture", "unit": "kg"},
    {"name": "Green Pepper", "name_amharic": "በርበሬ", "category": "horticulture", "unit": "kg"},
    {"name": "Lettuce", "name_amharic": "ሰላጣ", "category": "horticulture", "unit": "kg"},
    {"name": "Spinach", "name_amharic": "ቆስጣ", "category": "horticulture", "unit": "kg"},
    
    # Dairy products
    {"name": "Fresh Milk", "name_amharic": "አዲስ ወተት", "category": "dairy", "unit": "liter"},
    {"name": "Ayib", "name_amharic": "አይብ", "category": "dairy", "unit": "kg"},
    {"name": "Butter", "name_amharic": "ቅቤ", "category": "dairy", "unit": "kg"},
]

# Product knowledge base
PRODUCT_KNOWLEDGE = {
    "Red Onion": [
        "Store red onions in a cool, dry, well-ventilated place away from direct sunlight.",
        "Red onions contain quercetin, a powerful antioxidant that helps reduce inflammation.",
        "Red onions are rich in vitamin C and fiber, supporting immune system and digestion.",
        "Best season for red onions in Ethiopia is from October to March."
    ],
    "Tomato": [
        "Store tomatoes at room temperature until ripe, then refrigerate for longer shelf life.",
        "Tomatoes are rich in lycopene, which may help reduce the risk of heart disease.",
        "One medium tomato contains about 25 calories and is high in vitamin C.",
        "Tomato season in Ethiopia peaks from December to April."
    ],
    "Potato": [
        "Store potatoes in a cool, dark place to prevent sprouting and greening.",
        "Potatoes are a good source of potassium, vitamin C, and fiber.",
        "One medium potato contains about 110 calories and provides energy.",
        "Potatoes can be grown year-round in Ethiopia with proper irrigation."
    ],
    "Avocado": [
        "Store unripe avocados at room temperature, refrigerate when ripe.",
        "Avocados are high in healthy monounsaturated fats and fiber.",
        "One avocado contains about 320 calories and is rich in folate and vitamin K.",
        "Avocado season in Ethiopia is from March to September."
    ],
    "Banana": [
        "Store bananas at room temperature, refrigerate when ripe to slow ripening.",
        "Bananas are rich in potassium, vitamin B6, and natural sugars.",
        "One medium banana contains about 105 calories and provides quick energy.",
        "Bananas are available year-round in Ethiopia."
    ],
    "Fresh Milk": [
        "Store fresh milk in the refrigerator at 4°C or below.",
        "Fresh milk is rich in calcium, protein, and vitamin D.",
        "One liter of fresh milk contains about 600 calories and 32g protein.",
        "Fresh milk should be consumed within 3-5 days of purchase."
    ],
    "Ayib": [
        "Store Ayib in the refrigerator wrapped in cheesecloth or paper.",
        "Ayib is a traditional Ethiopian cheese rich in protein and calcium.",
        "Ayib contains probiotics that support gut health.",
        "Ayib can be used in various Ethiopian dishes like Gomen and Kitfo."
    ]
}

# Ethiopian locations
ETHIOPIAN_LOCATIONS = [
    "Addis Ababa", "Dire Dawa", "Bahir Dar", "Gondar", "Mekele",
    "Hawassa", "Jimma", "Harar", "Arba Minch", "Dessie"
]

def generate_users(db: Session, num_customers: int = 50, num_suppliers: int = 10):
    """Generate synthetic users (customers and suppliers)."""
    users = []
    
    # Generate customers
    for _ in range(num_customers):
        user = User(
            name=fake.first_name(),
            phone=fake.phone_number()[:15],
            user_type="customer",
            default_location=random.choice(ETHIOPIAN_LOCATIONS)
        )
        users.append(user)
        db.add(user)
    
    # Generate suppliers
    supplier_names = ["alem", "lema", "kasu", "girma", "mesfin", "tigist", "abebe", "chaltu", "dawit", "hana"]
    for i in range(num_suppliers):
        user = User(
            name=supplier_names[i] if i < len(supplier_names) else fake.first_name(),
            phone=fake.phone_number()[:15],
            user_type="supplier",
            default_location=random.choice(ETHIOPIAN_LOCATIONS)
        )
        users.append(user)
        db.add(user)
    
    db.commit()
    return users

def generate_products(db: Session, suppliers: list):
    """Generate products with suppliers."""
    products = []
    
    for product_data in PRODUCTS_DATA:
        # Assign random supplier
        supplier = random.choice([u for u in suppliers if u.user_type == "supplier"])
        
        # Generate base price based on category
        base_price = random.uniform(15, 80) if product_data["category"] == "horticulture" else random.uniform(25, 120)
        
        product = Product(
            name=product_data["name"],
            name_amharic=product_data["name_amharic"],
            category=product_data["category"],
            unit=product_data["unit"],
            description=f"Fresh {product_data['name'].lower()} from local farms",
            supplier_id=supplier.id,
            current_price=base_price,
            quantity_available=random.uniform(10, 100),
            expiry_date=datetime.utcnow() + timedelta(days=random.randint(1, 30))
        )
        products.append(product)
        db.add(product)
    
    db.commit()
    return products

def generate_pricing_history(db: Session, products: list, days_back: int = 365):
    """Generate 1-year historical pricing data."""
    market_types = ["local_shop", "supermarket", "distribution_center"]
    
    for product in products:
        base_price = product.current_price
        
        for days_ago in range(days_back):
            date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Generate price variations
            for market_type in market_types:
                # Price variations based on market type
                if market_type == "local_shop":
                    price_multiplier = random.uniform(0.7, 0.9)
                elif market_type == "supermarket":
                    price_multiplier = random.uniform(1.0, 1.2)
                else:  # distribution_center
                    price_multiplier = random.uniform(0.8, 1.0)
                
                # Seasonal variations
                seasonal_factor = 1.0
                if date.month in [12, 1, 2]:  # Dry season
                    seasonal_factor = random.uniform(1.1, 1.3)
                elif date.month in [6, 7, 8]:  # Rainy season
                    seasonal_factor = random.uniform(0.8, 1.0)
                
                price = base_price * price_multiplier * seasonal_factor
                
                pricing_record = PricingHistory(
                    product_id=product.id,
                    price=round(price, 2),
                    source_market_type=market_type,
                    location_detail=random.choice(ETHIOPIAN_LOCATIONS),
                    date=date
                )
                db.add(pricing_record)
    
    db.commit()

def generate_orders(db: Session, customers: list, products: list, days_back: int = 365):
    """Generate 1-year order history."""
    for days_ago in range(days_back):
        date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Generate 1-5 orders per day
        num_orders = random.randint(1, 5)
        
        for _ in range(num_orders):
            customer = random.choice([u for u in customers if u.user_type == "customer"])
            product = random.choice(products)
            
            quantity = random.uniform(0.5, 10)
            unit_price = product.current_price * random.uniform(0.9, 1.1)
            total_amount = quantity * unit_price
            
            order = Order(
                user_id=customer.id,
                product_id=product.id,
                quantity_ordered=quantity,
                unit_price=unit_price,
                total_amount=total_amount,
                delivery_date=date + timedelta(days=random.randint(1, 3)),
                delivery_location=customer.default_location,
                payment_method="COD",
                status=random.choice(["delivered", "confirmed", "pending"]),
                created_at=date
            )
            db.add(order)
    
    db.commit()

def generate_product_knowledge(db: Session, products: list):
    """Generate product knowledge base for RAG."""
    for product in products:
        if product.name in PRODUCT_KNOWLEDGE:
            for knowledge_text in PRODUCT_KNOWLEDGE[product.name]:
                knowledge_type = random.choice(["storage", "nutrition", "recipe", "seasonal"])
                
                knowledge = ProductKnowledge(
                    product_id=product.id,
                    knowledge_type=knowledge_type,
                    content=knowledge_text,
                    language="en"
                )
                db.add(knowledge)
    
    db.commit()

def main():
    """Main function to generate all synthetic data."""
    print("Starting synthetic data generation...")
    
    # Initialize database
    init_database()
    
    # Create database session
    db = SessionLocal()
    
    try:
        print("Generating users...")
        users = generate_users(db)
        customers = [u for u in users if u.user_type == "customer"]
        suppliers = [u for u in users if u.user_type == "supplier"]
        
        print("Generating products...")
        products = generate_products(db, suppliers)
        
        print("Generating pricing history (1 year)...")
        generate_pricing_history(db, products)
        
        print("Generating order history (1 year)...")
        generate_orders(db, customers, products)
        
        print("Generating product knowledge base...")
        generate_product_knowledge(db, products)
        
        print("Synthetic data generation completed successfully!")
        print(f"Generated: {len(users)} users, {len(products)} products")
        
    except Exception as e:
        print(f"Error generating data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
