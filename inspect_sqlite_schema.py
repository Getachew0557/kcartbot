#!/usr/bin/env python3
"""
SQLite Schema Inspector for KcartBot
====================================

This script inspects the SQLite database schema to understand
the actual column structure for migration to PostgreSQL.
"""

import sqlite3
import psycopg2
import os

def inspect_sqlite_schema():
    """Inspect SQLite database schema."""
    sqlite_path = "./kcartbot.db"
    
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        print("Please run 'python data/generate_data.py' first to create sample data.")
        return
    
    try:
        conn = psycopg2.connect(sqlite_path)
        cursor = conn.cursor()
        
        print("🔍 SQLite Database Schema Inspection")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        print()
        
        # Inspect each table
        for table_name in tables:
            print(f"📊 Table: {table_name}")
            print("-" * 30)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  {col_name}: {col_type} {'NOT NULL' if not_null else 'NULL'} {'PRIMARY KEY' if pk else ''}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                print("  Sample data:")
                for i, row in enumerate(sample_rows):
                    print(f"    Row {i+1}: {row}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting schema: {e}")

if __name__ == "__main__":
    inspect_sqlite_schema()

