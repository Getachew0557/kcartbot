"""Script to display generated data from KcartBot database."""

import sqlite3
import pandas as pd
import sys
import os

def show_database_data():
    """Display the generated database data."""
    
    # Connect to SQLite database
    conn = sqlite3.connect('kcartbot.db')
    
    print("=" * 60)
    print("KCARTBOT GENERATED DATA OVERVIEW")
    print("=" * 60)
    
    # Show Users
    print("\nUSERS (Customers & Suppliers)")
    print("-" * 40)
    users_df = pd.read_sql_query("""
        SELECT user_type, COUNT(*) as count 
        FROM users 
        GROUP BY user_type
    """, conn)
    print(users_df.to_string(index=False))
    
    # Show sample users
    print("\nSample Users:")
    sample_users = pd.read_sql_query("""
        SELECT name, phone, user_type, default_location, created_at
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """, conn)
    print(sample_users.to_string(index=False))
    
    # Show Products
    print("\n\nPRODUCTS")
    print("-" * 40)
    products_df = pd.read_sql_query("""
        SELECT category, COUNT(*) as count 
        FROM products 
        GROUP BY category
    """, conn)
    print(products_df.to_string(index=False))
    
    # Show sample products
    print("\nSample Products:")
    sample_products = pd.read_sql_query("""
        SELECT name, name_amharic, category, unit, current_price, quantity_available
        FROM products 
        ORDER BY created_at DESC 
        LIMIT 10
    """, conn)
    print(sample_products.to_string(index=False))
    
    # Show Orders
    print("\n\nORDERS")
    print("-" * 40)
    orders_df = pd.read_sql_query("""
        SELECT status, COUNT(*) as count 
        FROM orders 
        GROUP BY status
    """, conn)
    print(orders_df.to_string(index=False))
    
    # Show recent orders
    print("\nRecent Orders:")
    recent_orders = pd.read_sql_query("""
        SELECT o.created_at, u.name as customer_name, p.name as product_name, 
               o.quantity_ordered, o.unit_price, o.total_amount, o.status
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        ORDER BY o.created_at DESC 
        LIMIT 10
    """, conn)
    print(recent_orders.to_string(index=False))
    
    # Show Pricing History
    print("\n\nPRICING HISTORY")
    print("-" * 40)
    pricing_df = pd.read_sql_query("""
        SELECT source_market_type, COUNT(*) as count, 
               AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price
        FROM pricing_history 
        GROUP BY source_market_type
    """, conn)
    print(pricing_df.to_string(index=False))
    
    # Show Product Knowledge
    print("\n\nPRODUCT KNOWLEDGE")
    print("-" * 40)
    knowledge_df = pd.read_sql_query("""
        SELECT knowledge_type, COUNT(*) as count 
        FROM product_knowledge 
        GROUP BY knowledge_type
    """, conn)
    print(knowledge_df.to_string(index=False))
    
    # Show sample knowledge
    print("\nSample Knowledge:")
    sample_knowledge = pd.read_sql_query("""
        SELECT pk.knowledge_type, pk.content, p.name as product_name
        FROM product_knowledge pk
        JOIN products p ON pk.product_id = p.id
        ORDER BY pk.created_at DESC 
        LIMIT 5
    """, conn)
    for _, row in sample_knowledge.iterrows():
        print(f"\n{row['knowledge_type'].upper()}: {row['product_name']}")
        print(f"Content: {row['content'][:100]}...")
    
    # Show Statistics
    print("\n\nDATABASE STATISTICS")
    print("-" * 40)
    
    stats = {
        "Total Users": pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count'],
        "Total Products": pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn).iloc[0]['count'],
        "Total Orders": pd.read_sql_query("SELECT COUNT(*) as count FROM orders", conn).iloc[0]['count'],
        "Total Pricing Records": pd.read_sql_query("SELECT COUNT(*) as count FROM pricing_history", conn).iloc[0]['count'],
        "Total Knowledge Items": pd.read_sql_query("SELECT COUNT(*) as count FROM product_knowledge", conn).iloc[0]['count'],
    }
    
    for key, value in stats.items():
        print(f"{key}: {value:,}")
    
    # Show date ranges
    print("\nDATA DATE RANGES")
    print("-" * 40)
    
    date_ranges = pd.read_sql_query("""
        SELECT 
            'Orders' as table_name,
            MIN(created_at) as earliest,
            MAX(created_at) as latest
        FROM orders
        UNION ALL
        SELECT 
            'Pricing History' as table_name,
            MIN(date) as earliest,
            MAX(date) as latest
        FROM pricing_history
    """, conn)
    print(date_ranges.to_string(index=False))
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the API server: python src/main.py")
    print("2. Test the chat interface: python demo.py")
    print("3. Visit API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    show_database_data()