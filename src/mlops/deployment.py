"""Deployment management for models and services."""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    INACTIVE = "inactive"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    model_name: str
    model_version: str
    environment: str
    replicas: int
    resources: Dict[str, Any]
    health_check_endpoint: str
    rollback_version: Optional[str] = None


@dataclass
class DeploymentRecord:
    """Deployment record."""
    deployment_id: str
    config: DeploymentConfig
    status: DeploymentStatus
    created_at: datetime
    updated_at: datetime
    logs: List[str]
    health_status: Dict[str, Any]


class DeploymentManager:
    """Simple deployment manager for models and services."""
    
    def __init__(self, deployments_dir: str = "./deployments"):
        """Initialize deployment manager."""
        self.deployments_dir = deployments_dir
        self._ensure_deployments_dir()
        self._active_deployments: Dict[str, DeploymentRecord] = {}
    
    def _ensure_deployments_dir(self):
        """Ensure deployments directory exists."""
        os.makedirs(self.deployments_dir, exist_ok=True)
    
    def deploy_model(
        self,
        model_name: str,
        model_version: str,
        environment: str = "production",
        replicas: int = 1,
        resources: Dict[str, Any] = None,
        health_check_endpoint: str = "/health"
    ) -> str:
        """Deploy a model."""
        if resources is None:
            resources = {"cpu": "100m", "memory": "256Mi"}
        
        # Generate deployment ID
        deployment_id = f"{model_name}-{model_version}-{environment}-{int(time.time())}"
        
        # Create deployment configuration
        config = DeploymentConfig(
            model_name=model_name,
            model_version=model_version,
            environment=environment,
            replicas=replicas,
            resources=resources,
            health_check_endpoint=health_check_endpoint
        )
        
        # Create deployment record
        deployment = DeploymentRecord(
            deployment_id=deployment_id,
            config=config,
            status=DeploymentStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            logs=[],
            health_status={}
        )
        
        # Store deployment
        self._active_deployments[deployment_id] = deployment
        self._save_deployment(deployment)
        
        # Start deployment process
        self._deploy_async(deployment_id)
        
        return deployment_id
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment by ID."""
        return self._active_deployments.get(deployment_id)
    
    def list_deployments(
        self,
        model_name: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None
    ) -> List[DeploymentRecord]:
        """List deployments with optional filtering."""
        deployments = list(self._active_deployments.values())
        
        if model_name:
            deployments = [d for d in deployments if d.config.model_name == model_name]
        
        if environment:
            deployments = [d for d in deployments if d.config.environment == environment]
        
        if status:
            deployments = [d for d in deployments if d.status == status]
        
        return sorted(deployments, key=lambda x: x.created_at, reverse=True)
    
    def get_active_deployment(self, model_name: str, environment: str = "production") -> Optional[DeploymentRecord]:
        """Get active deployment for a model."""
        for deployment in self._active_deployments.values():
            if (deployment.config.model_name == model_name and 
                deployment.config.environment == environment and 
                deployment.status == DeploymentStatus.ACTIVE):
                return deployment
        return None
    
    def rollback_deployment(self, deployment_id: str, target_version: str) -> bool:
        """Rollback deployment to a previous version."""
        deployment = self._active_deployments.get(deployment_id)
        if not deployment:
            return False
        
        # Update status
        deployment.status = DeploymentStatus.ROLLING_BACK
        deployment.config.rollback_version = target_version
        deployment.updated_at = datetime.now()
        deployment.logs.append(f"Starting rollback to version {target_version}")
        
        self._save_deployment(deployment)
        
        # Simulate rollback process
        self._rollback_async(deployment_id)
        
        return True
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a deployment."""
        deployment = self._active_deployments.get(deployment_id)
        if not deployment:
            return False
        
        deployment.status = DeploymentStatus.INACTIVE
        deployment.updated_at = datetime.now()
        deployment.logs.append("Deployment stopped")
        
        self._save_deployment(deployment)
        return True
    
    def get_deployment_health(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment health status."""
        deployment = self._active_deployments.get(deployment_id)
        if not deployment:
            return {"status": "not_found"}
        
        # Simulate health check
        health_status = {
            "status": "healthy" if deployment.status == DeploymentStatus.ACTIVE else "unhealthy",
            "uptime": self._calculate_uptime(deployment),
            "replicas": {
                "desired": deployment.config.replicas,
                "running": deployment.config.replicas if deployment.status == DeploymentStatus.ACTIVE else 0,
                "healthy": deployment.config.replicas if deployment.status == DeploymentStatus.ACTIVE else 0
            },
            "last_check": datetime.now().isoformat()
        }
        
        deployment.health_status = health_status
        return health_status
    
    def get_deployment_logs(self, deployment_id: str, lines: int = 100) -> List[str]:
        """Get deployment logs."""
        deployment = self._active_deployments.get(deployment_id)
        if not deployment:
            return []
        
        return deployment.logs[-lines:] if lines > 0 else deployment.logs
    
    def scale_deployment(self, deployment_id: str, replicas: int) -> bool:
        """Scale deployment replicas."""
        deployment = self._active_deployments.get(deployment_id)
        if not deployment:
            return False
        
        old_replicas = deployment.config.replicas
        deployment.config.replicas = replicas
        deployment.updated_at = datetime.now()
        deployment.logs.append(f"Scaled from {old_replicas} to {replicas} replicas")
        
        self._save_deployment(deployment)
        return True
    
    def get_deployment_stats(self) -> Dict[str, Any]:
        """Get deployment statistics."""
        total_deployments = len(self._active_deployments)
        
        status_counts = {}
        for deployment in self._active_deployments.values():
            status = deployment.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        environments = set()
        models = set()
        for deployment in self._active_deployments.values():
            environments.add(deployment.config.environment)
            models.add(deployment.config.model_name)
        
        return {
            "total_deployments": total_deployments,
            "status_distribution": status_counts,
            "environments": list(environments),
            "models": list(models),
            "active_deployments": status_counts.get("active", 0)
        }
    
    def _deploy_async(self, deployment_id: str):
        """Asynchronous deployment process."""
        deployment = self._active_deployments[deployment_id]
        
        try:
            # Update status to deploying
            deployment.status = DeploymentStatus.DEPLOYING
            deployment.logs.append("Starting deployment...")
            self._save_deployment(deployment)
            
            # Simulate deployment steps
            time.sleep(2)  # Simulate deployment time
            
            deployment.logs.append("Pulling model artifacts...")
            time.sleep(1)
            
            deployment.logs.append("Starting containers...")
            time.sleep(1)
            
            deployment.logs.append("Running health checks...")
            time.sleep(1)
            
            # Mark as active
            deployment.status = DeploymentStatus.ACTIVE
            deployment.updated_at = datetime.now()
            deployment.logs.append("Deployment successful!")
            
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.updated_at = datetime.now()
            deployment.logs.append(f"Deployment failed: {str(e)}")
        
        self._save_deployment(deployment)
    
    def _rollback_async(self, deployment_id: str):
        """Asynchronous rollback process."""
        deployment = self._active_deployments[deployment_id]
        
        try:
            deployment.logs.append("Starting rollback...")
            time.sleep(1)
            
            deployment.logs.append("Stopping current version...")
            time.sleep(1)
            
            deployment.logs.append("Deploying previous version...")
            time.sleep(1)
            
            deployment.logs.append("Running health checks...")
            time.sleep(1)
            
            # Update to rolled back version
            deployment.config.model_version = deployment.config.rollback_version
            deployment.status = DeploymentStatus.ACTIVE
            deployment.updated_at = datetime.now()
            deployment.logs.append("Rollback successful!")
            
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.updated_at = datetime.now()
            deployment.logs.append(f"Rollback failed: {str(e)}")
        
        self._save_deployment(deployment)
    
    def _save_deployment(self, deployment: DeploymentRecord):
        """Save deployment to disk."""
        file_path = os.path.join(self.deployments_dir, f"{deployment.deployment_id}.json")
        
        deployment_data = {
            "deployment_id": deployment.deployment_id,
            "config": {
                "model_name": deployment.config.model_name,
                "model_version": deployment.config.model_version,
                "environment": deployment.config.environment,
                "replicas": deployment.config.replicas,
                "resources": deployment.config.resources,
                "health_check_endpoint": deployment.config.health_check_endpoint,
                "rollback_version": deployment.config.rollback_version
            },
            "status": deployment.status.value,
            "created_at": deployment.created_at.isoformat(),
            "updated_at": deployment.updated_at.isoformat(),
            "logs": deployment.logs,
            "health_status": deployment.health_status
        }
        
        with open(file_path, 'w') as f:
            json.dump(deployment_data, f, indent=2)
    
    def _calculate_uptime(self, deployment: DeploymentRecord) -> str:
        """Calculate deployment uptime."""
        if deployment.status != DeploymentStatus.ACTIVE:
            return "0s"
        
        uptime_seconds = (datetime.now() - deployment.created_at).total_seconds()
        
        if uptime_seconds < 60:
            return f"{int(uptime_seconds)}s"
        elif uptime_seconds < 3600:
            return f"{int(uptime_seconds / 60)}m"
        else:
            return f"{int(uptime_seconds / 3600)}h"

