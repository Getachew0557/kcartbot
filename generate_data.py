import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import random

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Ethiopian horticulture and dairy products
PRODUCTS = [
    {"name": "Red Onion", "category": "horticulture", "unit": "kg"},
    {"name": "Tomato", "category": "horticulture", "unit": "kg"},
    {"name": "Avocado", "category": "horticulture", "unit": "kg"},
    {"name": "Banana", "category": "horticulture", "unit": "kg"},
    {"name": "Mango", "category": "horticulture", "unit": "kg"},
    {"name": "Potato", "category": "horticulture", "unit": "kg"},
    {"name": "Cabbage", "category": "horticulture", "unit": "kg"},
    {"name": "Carrot", "category": "horticulture", "unit": "kg"},
    {"name": "Orange", "category": "horticulture", "unit": "kg"},
    {"name": "Lemon", "category": "horticulture", "unit": "kg"},
    {"name": "Milk", "category": "dairy", "unit": "liter"},
    {"name": "Ayib", "category": "dairy", "unit": "kg"},
    {"name": "Yogurt", "category": "dairy", "unit": "kg"},
    {"name": "Butter", "category": "dairy", "unit": "kg"},
    {"name": "Eggs", "category": "dairy", "unit": "dozen"}
]

SUPPLIERS = ["alem", "lema", "kasu", "girma", "mesfin", "tigist"]
LOCATIONS = ["Addis Ababa", "Dire Dawa", "Mekele", "Bahir Dar", "Hawassa", "Jimma"]
MARKET_TYPES = ["Local Shop", "Supermarket", "Distribution Center"]

def generate_products():
    products_data = []
    for product in PRODUCTS:
        products_data.append({
            "id": str(uuid.uuid4()),
            "name": product["name"],
            "category": product["category"],
            "unit": product["unit"],
            "current_price": round(random.uniform(20, 100), 2),
            "supplier_id": str(uuid.uuid4()),
            "stock_quantity": random.randint(50, 500)
        })
    return pd.DataFrame(products_data)

def generate_suppliers():
    suppliers_data = []
    for name in SUPPLIERS:
        suppliers_data.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "phone": f"09{random.randint(10000000, 99999999)}"
        })
    return pd.DataFrame(suppliers_data)

def generate_users():
    users_data = []
    ethiopian_names = ["hailat", "kidan", "sindayo", "kflay", "abel", "marta", "dawit", "yeshi"]
    for name in ethiopian_names:
        users_data.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "phone": f"09{random.randint(10000000, 99999999)}",
            "location": random.choice(LOCATIONS),
            "user_type": "customer"
        })
    return pd.DataFrame(users_data)

def generate_knowledge(products_df):
    knowledge_data = []
    
    knowledge_base = {
        "Red Onion": [
            ("How to store red onions?", "Store in a cool, dry, well-ventilated place. Keep away from potatoes.", "english"),
            ("የቀይ ሽንኩርት እንዴት እንደሚቆጠብ?", "ቀዝቃዛ፣ ደረቅ እና በደንብ የሚያየው ቦታ ውስጥ ያከማቹ። ከድንች ራቅ ይበሉ።", "amharic"),
            ("Red onion nutritional info?", "Low in calories, high in vitamin C and antioxidants.", "english")
        ],
        "Tomato": [
            ("How to store tomatoes?", "Store at room temperature until ripe, then refrigerate.", "english"),
            ("የቲማቲም እንዴት እንደሚቆጠብ?", "እስኪበስል ድረስ በክፍል ሙቀት ላይ ያከማቹ፣ ከዚያም በማቀዝቀዣ ውስጥ ያኑሩ።", "amharic"),
            ("Tomato recipes?", "Great for salads, sauces, stews, and fresh eating.", "english")
        ],
        "Avocado": [
            ("How to store ripe avocados?", "Refrigerate to slow down ripening. Use within 2-3 days.", "english"),
            ("የበሰለ አቮካዶ እንዴት እንደሚቆጠብ?", "ለማቃለል ለማቆየት በማቀዝቀዣ ውስጥ ያኑሩ። በ2-3 ቀናት ውስጥ ይጠቀሙ።", "amharic"),
            ("Avocado calories?", "Approximately 160 calories per 100g.", "english")
        ],
        "Milk": [
            ("How to store milk?", "Always refrigerate at 4°C or below. Use before expiry date.", "english"),
            ("ወተት እንዴት እንደሚቆጠብ?", "ሁልጊዜ በ4°C ወይም ከዚያ በታች በማቀዝቀዣ ውስጥ ያኑሩ። ከጊዜ አልባነት ቀን በፊት ይጠቀሙ።", "amharic"),
            ("Milk nutritional value?", "Rich in calcium, protein, and vitamins D and B12.", "english")
        ]
    }
    
    for product_name, knowledge_list in knowledge_base.items():
        product = products_df[products_df["name"] == product_name]
        if not product.empty:
            product_id = product.iloc[0]["id"]
            for question, answer, language in knowledge_list:
                knowledge_data.append({
                    "id": str(uuid.uuid4()),
                    "product_id": product_id,
                    "question": question,
                    "answer": answer,
                    "language": language
                })
    
    return pd.DataFrame(knowledge_data)

def generate_competitor_prices(products_df):
    competitor_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for product in products_df.to_dict('records'):
        current_date = start_date
        while current_date <= datetime.now():
            for market_type in MARKET_TYPES:
                # Base price varies by market type
                base_price = product["current_price"]
                if market_type == "Local Shop":
                    price_variation = random.uniform(-0.2, 0.1)  # Local shops often cheaper
                elif market_type == "Supermarket":
                    price_variation = random.uniform(-0.1, 0.3)  # Supermarkets slightly higher
                else:  # Distribution Center
                    price_variation = random.uniform(-0.3, 0.0)  # Wholesale prices
                
                final_price = max(10, base_price * (1 + price_variation))
                
                competitor_data.append({
                    "id": str(uuid.uuid4()),
                    "product_id": product["id"],
                    "date": current_date,
                    "price": round(final_price, 2),
                    "source_market_type": market_type,
                    "location_detail": random.choice(LOCATIONS),
                    "created_at": datetime.now()
                })
            
            # Move to next week
            current_date += timedelta(days=7)
    
    return pd.DataFrame(competitor_data)

def generate_transactions(products_df, users_df, suppliers_df):
    transactions_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1000):  # Generate 1000 transactions
        product = random.choice(products_df.to_dict('records'))
        user = random.choice(users_df.to_dict('records'))
        supplier = random.choice(suppliers_df.to_dict('records'))
        
        order_date = start_date + timedelta(days=random.randint(0, 365))
        quantity = random.randint(1, 10)
        price_per_unit = product["current_price"] * random.uniform(0.8, 1.2)
        total_amount = quantity * price_per_unit
        
        transactions_data.append({
            "id": str(uuid.uuid4()),
            "order_date": order_date,
            "user_id": user["id"],
            "user_name": user["name"],
            "phone": user["phone"],
            "supplier_id": supplier["id"],
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity_ordered": quantity,
            "unit": product["unit"],
            "price_per_unit": round(price_per_unit, 2),
            "order_total_amount": round(total_amount, 2),
            "delivery_date": order_date + timedelta(days=random.randint(1, 3)),
            "delivery_location": user["location"],
            "status": "completed"
        })
    
    return pd.DataFrame(transactions_data)

def main():
    print("Generating synthetic dataset...")
    
    # Create data directory
    import os
    os.makedirs("data", exist_ok=True)
    
    # Generate all datasets
    products_df = generate_products()
    suppliers_df = generate_suppliers()
    users_df = generate_users()
    knowledge_df = generate_knowledge(products_df)
    competitor_prices_df = generate_competitor_prices(products_df)
    transactions_df = generate_transactions(products_df, users_df, suppliers_df)
    
    # Save to CSV files
    products_df.to_csv("data/products.csv", index=False)
    suppliers_df.to_csv("data/suppliers.csv", index=False)
    users_df.to_csv("data/users.csv", index=False)
    knowledge_df.to_csv("data/knowledge.csv", index=False)
    competitor_prices_df.to_csv("data/competitor_prices.csv", index=False)
    transactions_df.to_csv("data/transactions.csv", index=False)
    
    print("Dataset generation completed!")
    print(f"Products: {len(products_df)} records")
    print(f"Suppliers: {len(suppliers_df)} records")
    print(f"Users: {len(users_df)} records")
    print(f"Knowledge: {len(knowledge_df)} records")
    print(f"Competitor Prices: {len(competitor_prices_df)} records")
    print(f"Transactions: {len(transactions_df)} records")

if __name__ == "__main__":
    main()