"""Model Registry for versioning and managing AI models."""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# SQLite implementation (commented out for PostgreSQL migration)
# import sqlite3
import psycopg2
# PostgreSQL implementation
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import settings


@dataclass
class ModelMetadata:
    """Model metadata structure."""
    model_id: str
    name: str
    version: str
    model_type: str  # 'chat', 'embedding', 'rag'
    file_path: str
    created_at: datetime
    performance_metrics: Dict[str, float]
    tags: List[str]
    description: str
    is_active: bool = True


class ModelRegistry:
    """PostgreSQL-based model registry for versioning and tracking models."""
    
    def __init__(self):
        """Initialize model registry with PostgreSQL."""
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_database()
    
    def _init_database(self):
        """Initialize the registry database."""
        with self.engine.connect() as conn:
            conn.execute(text("""
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
            """))
            conn.commit()
    
    def register_model(
        self,
        model_name: str,
        version: str,
        model_type: str,
        file_path: str,
        performance_metrics: Dict[str, float],
        tags: List[str] = None,
        description: str = ""
    ) -> str:
        """Register a new model version."""
        if tags is None:
            tags = []
        
        # Generate unique model ID
        model_id = self._generate_model_id(model_name, version)
        
        # Create model metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=model_name,
            version=version,
            model_type=model_type,
            file_path=file_path,
            created_at=datetime.now(),
            performance_metrics=performance_metrics,
            tags=tags,
            description=description
        )
        
        # Store in database
        with self.engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT INTO models 
                    (model_id, name, version, model_type, file_path, created_at, 
                     performance_metrics, tags, description, is_active)
                    VALUES (:model_id, :name, :version, :model_type, :file_path, :created_at, 
                            :performance_metrics, :tags, :description, :is_active)
                """), {
                    "model_id": metadata.model_id,
                    "name": metadata.name,
                    "version": metadata.version,
                    "model_type": metadata.model_type,
                    "file_path": metadata.file_path,
                    "created_at": metadata.created_at,
                    "performance_metrics": json.dumps(metadata.performance_metrics),
                    "tags": json.dumps(metadata.tags),
                    "description": metadata.description,
                    "is_active": metadata.is_active
                })
                conn.commit()
                return model_id
                
            except Exception as e:
                if "unique constraint" in str(e).lower():
                    raise ValueError(f"Model {model_name} version {version} already exists")
                raise e
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM models WHERE model_id = :model_id"), 
                                {"model_id": model_id})
            row = result.fetchone()
            
            if row:
                return self._row_to_metadata(row)
            return None
    
    def get_model_by_name_version(self, name: str, version: str) -> Optional[ModelMetadata]:
        """Get model metadata by name and version."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM models WHERE name = :name AND version = :version"), 
                                {"name": name, "version": version})
            row = result.fetchone()
            
            if row:
                return self._row_to_metadata(row)
            return None
    
    def list_models(
        self, 
        model_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[ModelMetadata]:
        """List all models with optional filtering."""
        query = "SELECT * FROM models WHERE 1=1"
        params = {}
        
        if model_type:
            query += " AND model_type = :model_type"
            params["model_type"] = model_type
        
        if active_only:
            query += " AND is_active = TRUE"
        
        query += " ORDER BY created_at DESC"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            return [self._row_to_metadata(row) for row in rows]
    
    def get_latest_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get the latest version of a model."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM models 
                WHERE name = :name AND is_active = TRUE 
                ORDER BY created_at DESC 
                LIMIT 1
            """), {"name": model_name})
            
            row = result.fetchone()
            
            if row:
                return self._row_to_metadata(row)
            return None
    
    def update_model_performance(self, model_id: str, metrics: Dict[str, float]) -> bool:
        """Update model performance metrics."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE models 
                SET performance_metrics = :metrics 
                WHERE model_id = :model_id
            """), {"metrics": json.dumps(metrics), "model_id": model_id})
            
            conn.commit()
            return result.rowcount > 0
    
    def deactivate_model(self, model_id: str) -> bool:
        """Deactivate a model."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE models 
                SET is_active = FALSE 
                WHERE model_id = :model_id
            """), {"model_id": model_id})
            
            conn.commit()
            return result.rowcount > 0
    
    def activate_model(self, model_id: str) -> bool:
        """Activate a model."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE models 
                SET is_active = TRUE 
                WHERE model_id = :model_id
            """), {"model_id": model_id})
            
            conn.commit()
            return result.rowcount > 0
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model from registry."""
        with self.engine.connect() as conn:
            result = conn.execute(text("DELETE FROM models WHERE model_id = :model_id"), 
                                {"model_id": model_id})
            conn.commit()
            return result.rowcount > 0
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self.engine.connect() as conn:
            # Total models
            result = conn.execute(text("SELECT COUNT(*) FROM models"))
            total_models = result.fetchone()[0]
            
            # Active models
            result = conn.execute(text("SELECT COUNT(*) FROM models WHERE is_active = TRUE"))
            active_models = result.fetchone()[0]
            
            # Models by type
            result = conn.execute(text("""
                SELECT model_type, COUNT(*) 
                FROM models 
                GROUP BY model_type
            """))
            models_by_type = dict(result.fetchall())
            
            # Models by name
            result = conn.execute(text("""
                SELECT name, COUNT(*) 
                FROM models 
                GROUP BY name
            """))
            models_by_name = dict(result.fetchall())
            
            return {
                "total_models": total_models,
                "active_models": active_models,
                "models_by_type": models_by_type,
                "models_by_name": models_by_name
            }
    
    def _generate_model_id(self, name: str, version: str) -> str:
        """Generate unique model ID."""
        content = f"{name}:{version}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _row_to_metadata(self, row) -> ModelMetadata:
        """Convert database row to ModelMetadata."""
        return ModelMetadata(
            model_id=row[0],
            name=row[1],
            version=row[2],
            model_type=row[3],
            file_path=row[4],
            created_at=row[5],
            performance_metrics=json.loads(row[6]),
            tags=json.loads(row[7]),
            description=row[8],
            is_active=bool(row[9])
        )

