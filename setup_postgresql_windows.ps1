# PowerShell PostgreSQL Setup Script for KcartBot
# ===============================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   KcartBot PostgreSQL Setup for Windows" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PostgreSQL is installed
$postgresPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
if (Test-Path $postgresPath) {
    Write-Host "✅ PostgreSQL found at: C:\Program Files\PostgreSQL\17\bin" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: PostgreSQL 17 not found at C:\Program Files\PostgreSQL\16\bin" -ForegroundColor Red
    Write-Host "Please install PostgreSQL 17 or update the path in this script" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install psycopg2-binary
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check PostgreSQL service
Write-Host "🔍 Checking PostgreSQL service..." -ForegroundColor Yellow
$service = Get-Service -Name "postgresql-x64-18" -ErrorAction SilentlyContinue
if ($service) {
    if ($service.Status -eq "Running") {
        Write-Host "✅ PostgreSQL service is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  PostgreSQL service is not running. Starting..." -ForegroundColor Yellow
        Start-Service -Name "postgresql-x64-18"
        Start-Sleep -Seconds 5
        if ((Get-Service -Name "postgresql-x64-18").Status -eq "Running") {
            Write-Host "✅ PostgreSQL service started successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to start PostgreSQL service" -ForegroundColor Red
            Write-Host "Please start the service manually and try again" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
} else {
    Write-Host "⚠️  PostgreSQL service not found. Please ensure PostgreSQL is installed correctly." -ForegroundColor Yellow
}

Write-Host ""

# Run PostgreSQL setup
Write-Host "🔧 Setting up PostgreSQL database..." -ForegroundColor Yellow
try {
    python windows_postgresql_setup.py --setup
    Write-Host "✅ PostgreSQL setup completed" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: PostgreSQL setup failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Migrate data
Write-Host "🔄 Migrating data from SQLite..." -ForegroundColor Yellow
try {
    python windows_postgresql_setup.py --migrate
    Write-Host "✅ Data migration completed" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Data migration failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Test connection
Write-Host "🧪 Testing PostgreSQL connection..." -ForegroundColor Yellow
try {
    python windows_postgresql_setup.py --test
    Write-Host "✅ PostgreSQL connection test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: PostgreSQL connection test failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Update environment file
Write-Host "📝 Updating environment configuration..." -ForegroundColor Yellow
try {
    python windows_postgresql_setup.py --all
    Write-Host "✅ Environment configuration updated" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Environment configuration update failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Setup completed successfully!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test MLOps components: python mlops_demo.py" -ForegroundColor White
Write-Host "2. Launch dashboard: python launch_dashboard.py" -ForegroundColor White
Write-Host "3. Open browser: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Manual commands available with:" -ForegroundColor Yellow
Write-Host "python windows_postgresql_setup.py --manual" -ForegroundColor White
Write-Host ""

# # Ask if user wants to test the application
# $testApp = Read-Host "Would you like to test the MLOps demo now? (y/n)"
# if ($testApp -eq "y" -or $testApp -eq "Y") {
#     Write-Host ""
#     Write-Host "🧪 Running MLOps demo..." -ForegroundColor Yellow
#     try {
#         python mlops_demo.py --component registry
#         Write-Host "✅ MLOps demo completed successfully" -ForegroundColor Green
#     } catch {
#         Write-Host "❌ MLOps demo failed" -ForegroundColor Red
#     }
# }

Write-Host ""
Read-Host "Press Enter to exit"
