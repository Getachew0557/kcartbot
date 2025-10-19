"""Performance monitoring and logging system."""

import json
import psycopg2
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

# PostgreSQL implementation
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import settings


@dataclass
class MetricEntry:
    """Metric entry structure."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]


@dataclass
class ModelPerformanceEntry:
    """Model performance entry structure."""
    timestamp: datetime
    model_name: str
    model_version: str
    metric_name: str
    value: float
    context: Dict[str, Any]


class PerformanceMonitor:
    """PostgreSQL-based performance monitoring system."""
    
    def __init__(self):
        """Initialize performance monitor with PostgreSQL."""
        # PostgreSQL implementation
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize the metrics database."""
        # PostgreSQL implementation
        with self.engine.connect() as conn:
            # System metrics table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    metric_name VARCHAR NOT NULL,
                    value REAL NOT NULL,
                    unit VARCHAR NOT NULL,
                    tags TEXT NOT NULL
                )
            """))
            
            # Model performance table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    model_name VARCHAR NOT NULL,
                    model_version VARCHAR NOT NULL,
                    metric_name VARCHAR NOT NULL,
                    value REAL NOT NULL,
                    context TEXT NOT NULL
                )
            """))
            
            # Create indexes for better performance
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_system_metric ON system_metrics(metric_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_model_timestamp ON model_performance(timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_model_name ON model_performance(model_name)"))
            
            conn.commit()
    
    def log_system_metric(
        self, 
        metric_name: str, 
        value: float, 
        unit: str = "count",
        tags: Dict[str, str] = None
    ):
        """Log a system metric."""
        if tags is None:
            tags = {}
        
        with self._lock:
            # PostgreSQL implementation
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO system_metrics 
                    (timestamp, metric_name, value, unit, tags)
                    VALUES (:timestamp, :metric_name, :value, :unit, :tags)
                """), {
                    "timestamp": datetime.now(),
                    "metric_name": metric_name,
                    "value": value,
                    "unit": unit,
                    "tags": json.dumps(tags)
                })
                conn.commit()
    
    def log_model_performance(
        self,
        model_name: str,
        model_version: str,
        metric_name: str,
        value: float,
        context: Dict[str, Any] = None
    ):
        """Log model performance metric."""
        if context is None:
            context = {}
        
        with self._lock:
            # PostgreSQL implementation
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO model_performance 
                    (timestamp, model_name, model_version, metric_name, value, context)
                    VALUES (:timestamp, :model_name, :model_version, :metric_name, :value, :context)
                """), {
                    "timestamp": datetime.now(),
                    "model_name": model_name,
                    "model_version": model_version,
                    "metric_name": metric_name,
                    "value": value,
                    "context": json.dumps(context)
                })
                conn.commit()
    
    def get_system_metrics(
        self,
        metric_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[MetricEntry]:
        """Get system metrics."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        query = "SELECT * FROM system_metrics WHERE timestamp >= :since_time"
        params = {"since_time": since_time}
        
        if metric_name:
            query += " AND metric_name = :metric_name"
            params["metric_name"] = metric_name
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        params["limit"] = limit
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            return [self._row_to_metric_entry(row) for row in rows]
    
    def get_model_performance(
        self,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        metric_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[ModelPerformanceEntry]:
        """Get model performance metrics."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        query = "SELECT * FROM model_performance WHERE timestamp >= :since_time"
        params = {"since_time": since_time}
        
        if model_name:
            query += " AND model_name = :model_name"
            params["model_name"] = model_name
        
        if model_version:
            query += " AND model_version = :model_version"
            params["model_version"] = model_version
        
        if metric_name:
            query += " AND metric_name = :metric_name"
            params["metric_name"] = metric_name
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        params["limit"] = limit
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            return [self._row_to_performance_entry(row) for row in rows]
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        with self.engine.connect() as conn:
            # System metrics summary
            result = conn.execute(text("""
                SELECT metric_name, AVG(value), MIN(value), MAX(value), COUNT(*)
                FROM system_metrics 
                WHERE timestamp >= :since_time
                GROUP BY metric_name
            """), {"since_time": since_time})
            
            system_summary = {}
            for row in result.fetchall():
                system_summary[row[0]] = {
                    "avg": row[1],
                    "min": row[2],
                    "max": row[3],
                    "count": row[4]
                }
            
            # Model performance summary
            result = conn.execute(text("""
                SELECT model_name, model_version, metric_name, AVG(value), COUNT(*)
                FROM model_performance 
                WHERE timestamp >= :since_time
                GROUP BY model_name, model_version, metric_name
            """), {"since_time": since_time})
            
            model_summary = defaultdict(lambda: defaultdict(dict))
            for row in result.fetchall():
                model_summary[row[0]][row[1]][row[2]] = {
                    "avg": row[3],
                    "count": row[4]
                }
            
            return {
                "period_hours": hours,
                "system_metrics": system_summary,
                "model_performance": dict(model_summary)
            }
    
    def get_metric_trends(
        self,
        metric_name: str,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get metric trends over time."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    timestamp as time_bucket,
                    AVG(value) as avg_value,
                    COUNT(*) as count
                FROM system_metrics 
                WHERE timestamp >= :since_time AND metric_name = :metric_name
                GROUP BY time_bucket
                ORDER BY time_bucket
            """), {"since_time": since_time, "metric_name": metric_name})
            
            trends = []
            for row in result.fetchall():
                trends.append({
                    "timestamp": row[0],
                    "avg_value": row[1],
                    "count": row[2]
                })
            
            return trends
    
    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics to prevent database bloat."""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        
        with self.engine.connect() as conn:
            # Clean system metrics
            result = conn.execute(text("""
                DELETE FROM system_metrics 
                WHERE timestamp < :cutoff_time
            """), {"cutoff_time": cutoff_time})
            
            system_deleted = result.rowcount
            
            # Clean model performance
            result = conn.execute(text("""
                DELETE FROM model_performance 
                WHERE timestamp < :cutoff_time
            """), {"cutoff_time": cutoff_time})
            
            model_deleted = result.rowcount
            
            conn.commit()
            
            return {
                "system_metrics_deleted": system_deleted,
                "model_performance_deleted": model_deleted,
                "cutoff_date": cutoff_time.isoformat()
            }
    
    def _row_to_metric_entry(self, row) -> MetricEntry:
        """Convert database row to MetricEntry."""
        return MetricEntry(
            timestamp=row[1],
            metric_name=row[2],
            value=row[3],
            unit=row[4],
            tags=json.loads(row[5])
        )
    
    def _row_to_performance_entry(self, row) -> ModelPerformanceEntry:
        """Convert database row to ModelPerformanceEntry."""
        return ModelPerformanceEntry(
            timestamp=row[1],
            model_name=row[2],
            model_version=row[3],
            metric_name=row[4],
            value=row[5],
            context=json.loads(row[6])
        )