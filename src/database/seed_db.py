import pandas as pd
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.database.models import User, Supplier, Product, ProductKnowledge, CompetitorPrice, Transaction
import uuid
from datetime import datetime

def seed_database():
    db = SessionLocal()
    
    try:
        # Clear existing data (in reverse order of dependencies)
        db.query(Transaction).delete()
        db.query(CompetitorPrice).delete()
        db.query(ProductKnowledge).delete()
        db.query(Product).delete()
        db.query(Supplier).delete()
        db.query(User).delete()
        db.commit()
        
        # Load and seed suppliers
        suppliers_df = pd.read_csv("data/suppliers.csv")
        for _, row in suppliers_df.iterrows():
            supplier = Supplier(
                id=row['id'],
                name=row['name'],
                phone=row['phone']
            )
            db.add(supplier)
        db.commit()
        print("Suppliers seeded successfully!")
        
        # Load and seed users
        users_df = pd.read_csv("data/users.csv")
        for _, row in users_df.iterrows():
            user = User(
                id=row['id'],
                name=row['name'],
                phone=row['phone'],
                location=row['location'],
                user_type=row['user_type']
            )
            db.add(user)
        db.commit()
        print("Users seeded successfully!")
        
        # Load and seed products
        products_df = pd.read_csv("data/products.csv")
        for _, row in products_df.iterrows():
            product = Product(
                id=row['id'],
                name=row['name'],
                category=row['category'],
                unit=row['unit'],
                current_price=row['current_price'],
                supplier_id=row['supplier_id'],
                stock_quantity=row['stock_quantity']
            )
            db.add(product)
        db.commit()
        print("Products seeded successfully!")
        
        # Load and seed knowledge base
        knowledge_df = pd.read_csv("data/knowledge.csv")
        for _, row in knowledge_df.iterrows():
            knowledge = ProductKnowledge(
                id=row['id'],
                product_id=row['product_id'],
                question=row['question'],
                answer=row['answer'],
                language=row['language']
            )
            db.add(knowledge)
        db.commit()
        print("Knowledge base seeded successfully!")
        
        # Load and seed competitor prices
        competitor_prices_df = pd.read_csv("data/competitor_prices.csv")
        for _, row in competitor_prices_df.iterrows():
            competitor_price = CompetitorPrice(
                id=row['id'],
                product_id=row['product_id'],
                date=datetime.fromisoformat(row['date'].replace('Z', '+00:00')),
                price=row['price'],
                source_market_type=row['source_market_type'],
                location_detail=row['location_detail']
            )
            db.add(competitor_price)
        db.commit()
        print("Competitor prices seeded successfully!")
        
        # Load and seed transactions
        transactions_df = pd.read_csv("data/transactions.csv")
        for _, row in transactions_df.iterrows():
            transaction = Transaction(
                id=row['id'],
                order_date=datetime.fromisoformat(row['order_date'].replace('Z', '+00:00')),
                user_id=row['user_id'],
                user_name=row['user_name'],
                phone=row['phone'],
                supplier_id=row['supplier_id'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                quantity_ordered=row['quantity_ordered'],
                unit=row['unit'],
                price_per_unit=row['price_per_unit'],
                order_total_amount=row['order_total_amount'],
                delivery_date=datetime.fromisoformat(row['delivery_date'].replace('Z', '+00:00')) if pd.notna(row['delivery_date']) else None,
                delivery_location=row['delivery_location'],
                status=row['status']
            )
            db.add(transaction)
        db.commit()
        print("Transactions seeded successfully!")
        
        print("All data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()