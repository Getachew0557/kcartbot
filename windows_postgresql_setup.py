#!/usr/bin/env python3
"""
Windows PostgreSQL Setup Script for KcartBot
=============================================

This script automates PostgreSQL setup on Windows for KcartBot.
It handles database creation, user setup, and data migration.

Usage:
    python windows_postgresql_setup.py [--setup] [--migrate] [--test] [--all]

Options:
    --setup     - Setup PostgreSQL database and user
    --migrate   - Migrate data from SQLite to PostgreSQL
    --test      - Test PostgreSQL connection
    --all       - Run all setup steps
    --help      - Show this help message
"""

import argparse
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlite3
from datetime import datetime
import json
import platform

# Windows-specific PostgreSQL configuration
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "root",
    "database": "kcartbot",
    "postgresql_path": r"C:\Program Files\PostgreSQL\17\bin"
}

SQLITE_DB_PATH = "./kcartbot.db"


def check_postgresql_installation():
    """Check if PostgreSQL is properly installed."""
    print("🔍 Checking PostgreSQL installation...")
    
    # Check if PostgreSQL bin directory exists
    if not os.path.exists(POSTGRES_CONFIG["postgresql_path"]):
        print(f"❌ PostgreSQL not found at: {POSTGRES_CONFIG['postgresql_path']}")
        print("Please install PostgreSQL 17 or update the path in the script.")
        return False
    
    # Check if psql command is available
    psql_path = os.path.join(POSTGRES_CONFIG["postgresql_path"], "psql.exe")
    if not os.path.exists(psql_path):
        print(f"❌ psql.exe not found at: {psql_path}")
        return False
    
    print(f"✅ PostgreSQL found at: {POSTGRES_CONFIG['postgresql_path']}")
    return True


def setup_postgresql_windows():
    """Setup PostgreSQL database and user on Windows."""
    print("🔧 Setting up PostgreSQL database on Windows...")
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_CONFIG['database']}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {POSTGRES_CONFIG['database']}")
            print(f"✅ Created database: {POSTGRES_CONFIG['database']}")
        else:
            print(f"✅ Database already exists: {POSTGRES_CONFIG['database']}")
        
        # Connect to the new database
        conn.close()
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            database=POSTGRES_CONFIG["database"]
        )
        cursor = conn.cursor()
        
        # Drop existing tables to recreate with correct schema
        drop_tables_windows(cursor)
        
        # Create tables with updated schema
        create_tables_windows(cursor)
        
        conn.commit()
        conn.close()
        
        print("✅ PostgreSQL setup completed successfully!")
        
    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("❌ Password authentication failed!")
            print("Please check your PostgreSQL password.")
            print("Default password might be different. Try:")
            print("1. Check pgAdmin for the password")
            print("2. Reset password: ALTER USER postgres PASSWORD 'root';")
            return False
        elif "could not connect to server" in str(e):
            print("❌ Could not connect to PostgreSQL server!")
            print("Please ensure PostgreSQL service is running:")
            print("1. Open Services (services.msc)")
            print("2. Find 'postgresql-x64-17' service")
            print("3. Start the service if it's not running")
            return False
        else:
            print(f"❌ Error setting up PostgreSQL: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


def drop_tables_windows(cursor):
    """Drop existing tables to recreate with correct schema."""
    print("🗑️  Dropping existing tables...")
    
    # Drop tables in reverse order to handle foreign key constraints
    tables_to_drop = [
        "health_results", "model_performance", "system_metrics", "models",
        "product_knowledge", "pricing_history", "orders", "products", "users"
    ]
    
    for table_name in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            print(f"  ✅ Dropped table: {table_name}")
        except Exception as e:
            print(f"  ⚠️  Could not drop {table_name}: {e}")


def create_tables_windows(cursor):
    """Create all necessary tables for Windows PostgreSQL."""
    print("📋 Creating database tables...")
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            phone VARCHAR UNIQUE NOT NULL,
            default_location VARCHAR,
            user_type VARCHAR DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            name_amharic VARCHAR,
            category VARCHAR NOT NULL,
            unit VARCHAR DEFAULT 'kg',
            description TEXT,
            supplier_id VARCHAR REFERENCES users(id),
            current_price REAL NOT NULL,
            quantity_available INTEGER DEFAULT 0,
            expiry_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR REFERENCES users(id),
            product_id VARCHAR REFERENCES products(id),
            quantity_ordered INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            delivery_date TIMESTAMP,
            delivery_location VARCHAR,
            payment_method VARCHAR,
            status VARCHAR DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Pricing history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pricing_history (
            id VARCHAR PRIMARY KEY,
            product_id VARCHAR REFERENCES products(id),
            price REAL NOT NULL,
            source_market_type VARCHAR,
            location_detail VARCHAR,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Product knowledge table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_knowledge (
            id VARCHAR PRIMARY KEY,
            product_id VARCHAR REFERENCES products(id),
            knowledge_type VARCHAR NOT NULL,
            content TEXT NOT NULL,
            language VARCHAR DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # MLOps tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            model_id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            version VARCHAR NOT NULL,
            model_type VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL,
            performance_metrics TEXT NOT NULL,
            tags TEXT NOT NULL,
            description TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(name, version)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            metric_name VARCHAR NOT NULL,
            value REAL NOT NULL,
            unit VARCHAR NOT NULL,
            tags TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_performance (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            model_name VARCHAR NOT NULL,
            model_version VARCHAR NOT NULL,
            metric_name VARCHAR NOT NULL,
            value REAL NOT NULL,
            context TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_results (
            id SERIAL PRIMARY KEY,
            check_name VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            message VARCHAR NOT NULL,
            details TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            response_time_ms REAL NOT NULL
        )
    """)
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)",
        "CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type)",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
        "CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
        "CREATE INDEX IF NOT EXISTS idx_pricing_product ON pricing_history(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_product ON product_knowledge(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_type ON product_knowledge(knowledge_type)",
        "CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_system_metric ON system_metrics(metric_name)",
        "CREATE INDEX IF NOT EXISTS idx_model_timestamp ON model_performance(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_model_name ON model_performance(model_name)",
        "CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_results(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_health_name ON health_results(check_name)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("✅ All tables and indexes created successfully!")


def migrate_data_windows():
    """Migrate data from SQLite to PostgreSQL on Windows."""
    print("🔄 Migrating data from SQLite to PostgreSQL...")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        print("Please run 'python data/generate_data.py' first to create sample data.")
        return False
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            database=POSTGRES_CONFIG["database"]
        )
        pg_cursor = pg_conn.cursor()
        
        # Get actual SQLite schema for each table
        tables_to_migrate = ["users", "products", "orders", "pricing_history", "product_knowledge"]
        
        for table_name in tables_to_migrate:
            try:
                # Get actual columns from SQLite
                sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
                sqlite_columns = [row[1] for row in sqlite_cursor.fetchall()]
                
                print(f"📦 Migrating table: {table_name}")
                print(f"  SQLite columns: {sqlite_columns}")
                
                if not sqlite_columns:
                    print(f"  ⚠️  Table {table_name} not found in SQLite")
                    continue
                
                # Get data from SQLite
                sqlite_cursor.execute(f"SELECT {', '.join(sqlite_columns)} FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"  ⚠️  No data found in {table_name}")
                    continue
                
                # Handle data type conversions for PostgreSQL
                converted_rows = []
                for row in rows:
                    converted_row = list(row)
                    
                    # Convert boolean fields (SQLite stores as 0/1, PostgreSQL needs true/false)
                    for i, col_name in enumerate(sqlite_columns):
                        if col_name == "is_active" and i < len(converted_row):
                            converted_row[i] = bool(converted_row[i])
                    
                    converted_rows.append(tuple(converted_row))
                
                # Insert into PostgreSQL with individual transaction handling
                placeholders = ', '.join(['%s'] * len(sqlite_columns))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(sqlite_columns)}) VALUES ({placeholders})"
                
                # Use individual transactions to prevent rollback issues
                pg_cursor.execute("BEGIN")
                try:
                    pg_cursor.executemany(insert_sql, converted_rows)
                    pg_cursor.execute("COMMIT")
                    print(f"  ✅ Migrated {len(converted_rows)} rows to {table_name}")
                except Exception as insert_error:
                    pg_cursor.execute("ROLLBACK")
                    raise insert_error
                
            except Exception as e:
                print(f"  ❌ Error migrating {table_name}: {e}")
                # Try to get more details about the error
                if "no such column" in str(e):
                    print(f"  💡 Hint: Column mismatch - PostgreSQL schema needs updating")
                elif "boolean" in str(e) and "integer" in str(e):
                    print(f"  💡 Hint: Data type mismatch - boolean conversion needed")
                elif "current transaction is aborted" in str(e):
                    print(f"  💡 Hint: Transaction rollback - previous error caused this")
                continue
        
        pg_conn.commit()
        sqlite_conn.close()
        pg_conn.close()
        
        print("✅ Data migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error migrating data: {e}")
        return False
    
    return True


def migrate_table_windows(sqlite_cursor, pg_cursor, table_name, columns):
    """Migrate a single table from SQLite to PostgreSQL on Windows."""
    print(f"📦 Migrating table: {table_name}")
    
    try:
        # Get data from SQLite
        sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  ⚠️  No data found in {table_name}")
            return
        
        # Handle data type conversions for PostgreSQL
        converted_rows = []
        for row in rows:
            converted_row = list(row)
            
            # Convert boolean fields (SQLite stores as 0/1, PostgreSQL needs true/false)
            if table_name == "users" and len(converted_row) > 6:
                # Convert is_active from integer to boolean
                converted_row[6] = bool(converted_row[6])
            elif table_name == "products" and len(converted_row) > 10:
                # Convert is_active from integer to boolean
                converted_row[10] = bool(converted_row[10])
            
            converted_rows.append(tuple(converted_row))
        
        # Insert into PostgreSQL
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        pg_cursor.executemany(insert_sql, converted_rows)
        print(f"  ✅ Migrated {len(converted_rows)} rows to {table_name}")
        
    except Exception as e:
        print(f"  ❌ Error migrating {table_name}: {e}")
        # Try to get more details about the error
        if "no such column" in str(e):
            print(f"  💡 Hint: Column mismatch - check SQLite schema")
        elif "boolean" in str(e) and "integer" in str(e):
            print(f"  💡 Hint: Data type mismatch - boolean conversion needed")


def test_postgresql_windows():
    """Test PostgreSQL connection on Windows."""
    print("🧪 Testing PostgreSQL connection on Windows...")
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            database=POSTGRES_CONFIG["database"]
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connection successful!")
        print(f"   Version: {version}")
        
        # Test table existence
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tables: {', '.join(tables)}")
        
        # Test data counts
        for table in ['users', 'products', 'orders']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} rows")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False
    
    return True


def update_env_file_windows():
    """Update .env file with PostgreSQL configuration for Windows."""
    print("📝 Updating environment configuration...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ Environment file not found: {env_file}")
        print("Creating .env file from template...")
        try:
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from env.example")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update database URL
        updated_lines = []
        for line in lines:
            if line.startswith("DATABASE_URL="):
                updated_lines.append("DATABASE_URL=postgresql://postgres:root@localhost:5432/kcartbot\n")
            else:
                updated_lines.append(line)
        
        # Write updated .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ Environment file updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating environment file: {e}")
        return False
    
    return True


def run_manual_commands():
    """Display manual PostgreSQL setup commands for Windows."""
    print("\n📋 MANUAL POSTGRESQL SETUP COMMANDS")
    print("=" * 50)
    
    print("\n1️⃣ **Open Command Prompt as Administrator**")
    print("   - Press Win + R, type 'cmd', press Ctrl + Shift + Enter")
    
    print("\n2️⃣ **Navigate to PostgreSQL bin directory**")
    print(f"   cd \"{POSTGRES_CONFIG['postgresql_path']}\"")
    
    print("\n3️⃣ **Connect to PostgreSQL**")
    print(f"   psql -U postgres -p {POSTGRES_CONFIG['port']}")
    
    print("\n4️⃣ **Create database and user**")
    print("   CREATE DATABASE kcartbot;")
    print("   CREATE USER postgres WITH PASSWORD 'root';")
    print("   GRANT ALL PRIVILEGES ON DATABASE kcartbot TO postgres;")
    print("   \\q")
    
    print("\n5️⃣ **Test connection**")
    print(f"   psql -U postgres -d kcartbot -p {POSTGRES_CONFIG['port']}")
    print("   \\dt")
    print("   \\q")
    
    print("\n6️⃣ **Alternative: Use pgAdmin**")
    print("   - Open pgAdmin")
    print("   - Connect to PostgreSQL server")
    print("   - Right-click 'Databases' → Create → Database")
    print("   - Name: kcartbot")
    print("   - Owner: postgres")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Windows PostgreSQL Setup Script for KcartBot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup PostgreSQL database and user"
    )
    
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate data from SQLite to PostgreSQL"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test PostgreSQL connection"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all setup steps"
    )
    
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Show manual setup commands"
    )
    
    args = parser.parse_args()
    
    if not any([args.setup, args.migrate, args.test, args.all, args.manual]):
        parser.print_help()
        return
    
    print("🐘 KcartBot PostgreSQL Setup for Windows")
    print("=" * 50)
    print(f"PostgreSQL Path: {POSTGRES_CONFIG['postgresql_path']}")
    print(f"Database: {POSTGRES_CONFIG['database']}")
    print(f"User: {POSTGRES_CONFIG['user']}")
    print(f"Password: {POSTGRES_CONFIG['password']}")
    
    if args.manual:
        run_manual_commands()
        return
    
    success = True
    
    if args.all or args.setup:
        if not check_postgresql_installation():
            print("\n❌ PostgreSQL installation check failed!")
            print("Please install PostgreSQL 17 or update the path in the script.")
            return
        
        success &= setup_postgresql_windows()
    
    if args.all or args.migrate:
        success &= migrate_data_windows()
    
    if args.all or args.test:
        success &= test_postgresql_windows()
    
    if args.all:
        success &= update_env_file_windows()
    
    if success:
        print("\n🎉 PostgreSQL setup completed successfully!")
        print("\nNext steps:")
        print("1. Install Python dependencies: pip install psycopg2-binary")
        print("2. Test the application: python mlops_demo.py")
        print("3. Launch dashboard: python launch_dashboard.py")
        print("\nManual commands available with: --manual")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        print("Try manual setup with: --manual")
        sys.exit(1)


if __name__ == "__main__":
    main()
