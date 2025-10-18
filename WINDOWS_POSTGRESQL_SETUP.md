# Windows PostgreSQL Setup Guide for KcartBot

## 🪟 Complete Windows Setup Instructions

### 📋 **Prerequisites**

1. **PostgreSQL 18 Installed** at `C:\Program Files\PostgreSQL\18\bin`
2. **Python 3.9+** installed
3. **KcartBot project** cloned/downloaded

---

## 🚀 **Method 1: Automated Script Setup**

### **Step 1: Install Python Dependencies**
```cmd
# Open Command Prompt in project directory
pip install psycopg2-binary
pip install -r requirements.txt
```

### **Step 2: Run Automated Setup**
```cmd
# Run complete setup
python windows_postgresql_setup.py --all

# Or run individual steps
python windows_postgresql_setup.py --setup
python windows_postgresql_setup.py --migrate
python windows_postgresql_setup.py --test
```

### **Step 3: Test the Application**
```cmd
# Test MLOps components
python mlops_demo.py --component registry
python mlops_demo.py --component monitoring

# Launch dashboard
python launch_dashboard.py
```

---

## 🔧 **Method 2: Manual Setup**

### **Step 1: Start PostgreSQL Service**
```cmd
# Open Command Prompt as Administrator
# Start PostgreSQL service
net start postgresql-x64-18

# Or use Services Manager
# Press Win + R, type 'services.msc'
# Find 'postgresql-x64-18' and start it
```

### **Step 2: Open PostgreSQL Command Line**
```cmd
# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\18\bin"

# Connect to PostgreSQL
psql -U postgres
```

### **Step 3: Create Database and User**
```sql
-- Create database
CREATE DATABASE kcartbot;

-- Create user (if not exists)
CREATE USER postgres WITH PASSWORD 'root';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kcartbot TO postgres;

-- Exit psql
\q
```

### **Step 4: Test Connection**
```cmd
# Test connection to new database
psql -U postgres -d kcartbot

-- List tables (should be empty initially)
\dt

-- Exit
\q
```

### **Step 5: Update Environment File**
```cmd
# Edit .env file
notepad .env

# Update DATABASE_URL line to:
DATABASE_URL=postgresql://postgres:root@localhost:5433/kcartbot
```

### **Step 6: Run Migration**
```cmd
# Generate sample data (if not exists)
python data/generate_data.py

# Run migration
python postgresql_migration.py --setup
python postgresql_migration.py --migrate
python postgresql_migration.py --test
```

---

## 🧪 **Method 3: Using pgAdmin (GUI)**

### **Step 1: Open pgAdmin**
- Find pgAdmin in Start Menu
- Connect to PostgreSQL server

### **Step 2: Create Database**
1. Right-click "Databases" → "Create" → "Database"
2. Name: `kcartbot`
3. Owner: `postgres`
4. Click "Save"

### **Step 3: Create User (if needed)**
1. Right-click "Login/Group Roles" → "Create" → "Login/Group Role"
2. Name: `postgres`
3. Password: `root`
4. Click "Save"

### **Step 4: Test Connection**
1. Right-click "kcartbot" database → "Query Tool"
2. Run: `SELECT version();`
3. Should return PostgreSQL version

---

## 🔍 **Testing and Validation**

### **Test 1: Connection Test**
```cmd
python windows_postgresql_setup.py --test
```

**Expected Output:**
```
✅ PostgreSQL connection successful!
   Version: PostgreSQL 18.x
   Tables: users, products, orders, ...
   users: 50 rows
   products: 15 rows
   orders: 100 rows
```

### **Test 2: MLOps Components**
```cmd
python mlops_demo.py --component registry
python mlops_demo.py --component monitoring
python mlops_demo.py --component health
```

### **Test 3: Full Application**
```cmd
python launch_dashboard.py
# Open browser: http://localhost:8501
```

### **Test 4: Database Queries**
```cmd
# Connect to database
psql -U postgres -d kcartbot

-- Test queries
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM models;
SELECT COUNT(*) FROM system_metrics;
SELECT COUNT(*) FROM health_results;

-- Exit
\q
```

---

## 🚨 **Troubleshooting**

### **Issue 1: PostgreSQL Service Not Running**
```cmd
# Check service status
sc query postgresql-x64-18

# Start service
net start postgresql-x64-18

# Or use Services Manager
services.msc
```

### **Issue 2: Authentication Failed**
```cmd
# Connect as postgres user
psql -U postgres

# Reset password
ALTER USER postgres PASSWORD 'root';

# Exit
\q
```

### **Issue 3: Database Connection Refused**
```cmd
# Check if PostgreSQL is listening
netstat -an | findstr 5433

# Check PostgreSQL configuration
# Edit: C:\Program Files\PostgreSQL\18\data\postgresql.conf
# Ensure: listen_addresses = 'localhost'
```

### **Issue 4: Permission Denied**
```cmd
# Run Command Prompt as Administrator
# Or check pg_hba.conf file
# C:\Program Files\PostgreSQL\18\data\pg_hba.conf
```

### **Issue 5: Python Dependencies**
```cmd
# Install missing packages
pip install psycopg2-binary
pip install sqlalchemy
pip install pandas
pip install streamlit
```

---

## 📊 **Verification Checklist**

- [ ] PostgreSQL service is running
- [ ] Database `kcartbot` exists
- [ ] User `postgres` with password `root` exists
- [ ] All tables created successfully
- [ ] Data migrated from SQLite
- [ ] Environment file updated
- [ ] Python dependencies installed
- [ ] MLOps components working
- [ ] Dashboard accessible at http://localhost:8501

---

## 🎯 **Quick Commands Summary**

### **Automated Setup**
```cmd
# Complete setup
python windows_postgresql_setup.py --all

# Individual steps
python windows_postgresql_setup.py --setup
python windows_postgresql_setup.py --migrate
python windows_postgresql_setup.py --test

# Show manual commands
python windows_postgresql_setup.py --manual
```

### **Manual Setup**
```cmd
# Start service
net start postgresql-x64-18

# Connect to PostgreSQL
cd "C:\Program Files\PostgreSQL\18\bin"
psql -U postgres

# Create database
CREATE DATABASE kcartbot;
\q

# Test connection
psql -U postgres -d kcartbot
\dt
\q
```

### **Testing**
```cmd
# Test connection
python windows_postgresql_setup.py --test

# Test MLOps
python mlops_demo.py

# Launch dashboard
python launch_dashboard.py
```

---

## 📝 **Environment Configuration**

### **.env File**
```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql://postgres:root@localhost:5433/kcartbot

# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### **Alternative PostgreSQL URLs**
```bash
# With psycopg2
DATABASE_URL=postgresql+psycopg2://postgres:root@localhost:5433/kcartbot

# With asyncpg
DATABASE_URL=postgresql+asyncpg://postgres:root@localhost:5433/kcartbot
```

---

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

1. **PostgreSQL Connection**: ✅ Successful
2. **Database Tables**: ✅ All created
3. **Data Migration**: ✅ Completed
4. **MLOps Demo**: ✅ All components working
5. **Dashboard**: ✅ Accessible at http://localhost:8501
6. **API**: ✅ Working at http://localhost:8000

---

**Setup Status**: Ready for Windows PostgreSQL 18  
**Database**: kcartbot  
**User**: postgres  
**Password**: root  
**Port**: 5433
