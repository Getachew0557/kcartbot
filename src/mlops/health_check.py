"""Health checking and alerting system."""

import time
import requests
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# PostgreSQL implementation
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import settings


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable[[], Dict[str, Any]]
    interval_seconds: int = 60
    timeout_seconds: int = 30
    enabled: bool = True


@dataclass
class HealthResult:
    """Health check result."""
    check_name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    response_time_ms: float


class HealthChecker:
    """PostgreSQL-based health checking and alerting system."""
    
    def __init__(self):
        """Initialize health checker with PostgreSQL."""
        # PostgreSQL implementation
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_database()
        self._health_checks: Dict[str, HealthCheck] = {}
        self._register_default_checks()
    
    def _init_database(self):
        """Initialize the health database."""
        # PostgreSQL implementation
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS health_results (
                    id SERIAL PRIMARY KEY,
                    check_name VARCHAR NOT NULL,
                    status VARCHAR NOT NULL,
                    message VARCHAR NOT NULL,
                    details TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    response_time_ms REAL NOT NULL
                )
            """))
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_results(timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_health_name ON health_results(check_name)"))
            
            conn.commit()
    
    def _register_default_checks(self):
        """Register default health checks."""
        # System resource checks
        self.register_check("cpu_usage", self._check_cpu_usage, interval_seconds=30)
        self.register_check("memory_usage", self._check_memory_usage, interval_seconds=30)
        self.register_check("disk_usage", self._check_disk_usage, interval_seconds=60)
        
        # Database checks
        self.register_check("database_connection", self._check_database_connection, interval_seconds=60)
        self.register_check("vector_db_connection", self._check_vector_db_connection, interval_seconds=60)
        
        # API checks
        self.register_check("gemini_api", self._check_gemini_api, interval_seconds=120)
    
    def register_check(
        self,
        name: str,
        check_function: Callable[[], Dict[str, Any]],
        interval_seconds: int = 60,
        timeout_seconds: int = 30,
        enabled: bool = True
    ):
        """Register a health check."""
        self._health_checks[name] = HealthCheck(
            name=name,
            check_function=check_function,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            enabled=enabled
        )
    
    def run_check(self, check_name: str) -> HealthResult:
        """Run a specific health check."""
        check = self._health_checks.get(check_name)
        if not check:
            return HealthResult(
                check_name=check_name,
                status=HealthStatus.UNKNOWN,
                message="Check not found",
                details={},
                timestamp=datetime.now(),
                response_time_ms=0
            )
        
        start_time = time.time()
        
        try:
            result = check.check_function()
            
            # Determine status based on result
            status = HealthStatus.HEALTHY
            if result.get("status") == "warning":
                status = HealthStatus.WARNING
            elif result.get("status") == "critical":
                status = HealthStatus.CRITICAL
            
            response_time = (time.time() - start_time) * 1000
            
            health_result = HealthResult(
                check_name=check_name,
                status=status,
                message=result.get("message", "OK"),
                details=result.get("details", {}),
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
            
            # Store result
            self._store_health_result(health_result)
            
            return health_result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_result = HealthResult(
                check_name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
            
            self._store_health_result(health_result)
            return health_result
    
    def run_all_checks(self) -> Dict[str, HealthResult]:
        """Run all registered health checks."""
        results = {}
        
        for check_name in self._health_checks:
            if self._health_checks[check_name].enabled:
                results[check_name] = self.run_check(check_name)
        
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        results = self.run_all_checks()
        
        # Count statuses
        status_counts = {}
        for result in results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        if status_counts.get("critical", 0) > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts.get("warning", 0) > 0:
            overall_status = HealthStatus.WARNING
        
        return {
            "overall_status": overall_status.value,
            "status_counts": status_counts,
            "total_checks": len(results),
            "timestamp": datetime.now().isoformat(),
            "checks": {name: {
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms
            } for name, result in results.items()}
        }
    
    def get_health_history(
        self,
        check_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[HealthResult]:
        """Get health check history."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        query = "SELECT * FROM health_results WHERE timestamp >= :since_time"
        params = {"since_time": since_time}
        
        if check_name:
            query += " AND check_name = :check_name"
            params["check_name"] = check_name
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        params["limit"] = limit
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            return [self._row_to_health_result(row) for row in rows]
    
    def get_failing_checks(self, hours: int = 1) -> List[HealthResult]:
        """Get checks that have been failing."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM health_results 
                WHERE timestamp >= :since_time AND status IN ('warning', 'critical')
                ORDER BY timestamp DESC
            """), {"since_time": since_time})
            
            rows = result.fetchall()
            
            return [self._row_to_health_result(row) for row in rows]
    
    def cleanup_old_results(self, days_to_keep: int = 7):
        """Clean up old health check results."""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM health_results 
                WHERE timestamp < :cutoff_time
            """), {"cutoff_time": cutoff_time})
            
            deleted_count = result.rowcount
            conn.commit()
            
            return {"deleted_count": deleted_count, "cutoff_date": cutoff_time.isoformat()}
    
    # Default health check implementations
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        status = "healthy"
        if cpu_percent > 90:
            status = "critical"
        elif cpu_percent > 80:
            status = "warning"
        
        return {
            "status": status,
            "message": f"CPU usage: {cpu_percent:.1f}%",
            "details": {"cpu_percent": cpu_percent}
        }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        status = "healthy"
        if memory_percent > 95:
            status = "critical"
        elif memory_percent > 85:
            status = "warning"
        
        return {
            "status": status,
            "message": f"Memory usage: {memory_percent:.1f}%",
            "details": {
                "memory_percent": memory_percent,
                "available_gb": memory.available / (1024**3),
                "total_gb": memory.total / (1024**3)
            }
        }
    
    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage."""
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        status = "healthy"
        if disk_percent > 95:
            status = "critical"
        elif disk_percent > 85:
            status = "warning"
        
        return {
            "status": status,
            "message": f"Disk usage: {disk_percent:.1f}%",
            "details": {
                "disk_percent": disk_percent,
                "free_gb": disk.free / (1024**3),
                "total_gb": disk.total / (1024**3)
            }
        }
    
    def _check_database_connection(self) -> Dict[str, Any]:
        """Check database connection."""
        try:
            # Use SQLAlchemy to test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return {
                "status": "healthy",
                "message": "Database connection OK",
                "details": {}
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Database connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_vector_db_connection(self) -> Dict[str, Any]:
        """Check vector database connection."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path="./chroma_db")
            collections = client.list_collections()
            
            return {
                "status": "healthy",
                "message": f"Vector DB connection OK ({len(collections)} collections)",
                "details": {"collections": len(collections)}
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Vector DB connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_gemini_api(self) -> Dict[str, Any]:
        """Check Gemini API connectivity."""
        try:
            import google.generativeai as genai
            from config import settings
            
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Simple test request
            response = model.generate_content("Hello")
            
            if response and hasattr(response, 'text'):
                return {
                    "status": "healthy",
                    "message": "Gemini API connection OK",
                    "details": {}
                }
            else:
                return {
                    "status": "warning",
                    "message": "Gemini API responded but no text",
                    "details": {}
                }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Gemini API connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _store_health_result(self, result: HealthResult):
        """Store health result in database."""
        # PostgreSQL implementation
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO health_results 
                (check_name, status, message, details, timestamp, response_time_ms)
                VALUES (:check_name, :status, :message, :details, :timestamp, :response_time_ms)
            """), {
                "check_name": result.check_name,
                "status": result.status.value,
                "message": result.message,
                "details": str(result.details),
                "timestamp": result.timestamp,
                "response_time_ms": result.response_time_ms
            })
            conn.commit()
    
    def _row_to_health_result(self, row) -> HealthResult:
        """Convert database row to HealthResult."""
        return HealthResult(
            check_name=row[1],
            status=HealthStatus(row[2]),
            message=row[3],
            details=eval(row[4]) if row[4] else {},
            timestamp=row[5],
            response_time_ms=row[6]
        )