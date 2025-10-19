#!/usr/bin/env python3
"""
KcartBot MLOps Demonstration
============================

This script demonstrates the MLOps capabilities of KcartBot including:
- Model Registry operations
- Deployment management
- Performance monitoring
- Health checking
- Integration workflows

Usage:
    python mlops_demo.py [--component COMPONENT] [--interactive]

Components:
    registry     - Model registry operations
    deployment   - Deployment management
    monitoring   - Performance monitoring
    health       - Health checking
    all          - Run all components (default)
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime, timedelta
import json
import psycopg2

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.mlops.model_registry import ModelRegistry
from src.mlops.deployment import DeploymentManager, DeploymentStatus
from src.mlops.monitoring import PerformanceMonitor
from src.mlops.health_check import HealthChecker


class MLOpsDemo:
    """MLOps demonstration class."""
    
    def __init__(self):
        """Initialize MLOps components."""
        self.registry = ModelRegistry()
        self.deployment = DeploymentManager()
        self.monitoring = PerformanceMonitor()
        self.health = HealthChecker()
        
    def demo_model_registry(self):
        """Demonstrate model registry operations."""
        print("\n🏗️  MODEL REGISTRY DEMONSTRATION")
        print("=" * 50)
        
        # Register sample models
        print("📝 Registering sample models...")
        
        models = [
            {
                "model_name": "chat-model",
                "version": "1.0.0",
                "model_type": "chat",
                "file_path": "./models/chat_model_v1.pkl",
                "performance_metrics": {"accuracy": 0.95, "latency_ms": 120, "throughput": 100},
                "tags": ["production", "chat", "gemini"],
                "description": "Main chat model for customer interactions"
            },
            {
                "model_name": "rag-model",
                "version": "1.2.0",
                "model_type": "rag",
                "file_path": "./models/rag_model_v1.2.pkl",
                "performance_metrics": {"recall": 0.88, "precision": 0.92, "latency_ms": 200},
                "tags": ["production", "rag", "semantic-search"],
                "description": "RAG model for knowledge retrieval"
            },
            {
                "model_name": "pricing-model",
                "version": "2.0.0",
                "model_type": "prediction",
                "file_path": "./models/pricing_model_v2.pkl",
                "performance_metrics": {"mae": 0.15, "rmse": 0.23, "r2": 0.87},
                "tags": ["production", "pricing", "regression"],
                "description": "Price prediction model for market analysis"
            }
        ]
        
        registered_models = []
        for model_data in models:
            try:
                model_id = self.registry.register_model(**model_data)
                registered_models.append(model_id)
                print(f"✅ Registered {model_data['model_name']} v{model_data['version']} (ID: {model_id[:8]}...)")
            except Exception as e:
                print(f"❌ Failed to register {model_data['model_name']}: {e}")
        
        # List models
        print("\n📋 Listing all models:")
        all_models = self.registry.list_models()
        for model in all_models:
            print(f"  • {model.name} v{model.version} ({model.model_type}) - {'Active' if model.is_active else 'Inactive'}")
        
        # Get model statistics
        print("\n📊 Model registry statistics:")
        stats = self.registry.get_model_stats()
        print(f"  • Total models: {stats['total_models']}")
        print(f"  • Active models: {stats['active_models']}")
        print(f"  • Models by type: {stats['models_by_type']}")
        
        # Update model performance
        if registered_models:
            print(f"\n🔄 Updating performance metrics for {registered_models[0][:8]}...")
            new_metrics = {"accuracy": 0.96, "latency_ms": 110, "throughput": 105}
            success = self.registry.update_model_performance(registered_models[0], new_metrics)
            print(f"  {'✅' if success else '❌'} Performance update {'successful' if success else 'failed'}")
        
        return registered_models
    
    def demo_deployment(self, model_ids=None):
        """Demonstrate deployment management."""
        print("\n🚀 DEPLOYMENT MANAGEMENT DEMONSTRATION")
        print("=" * 50)
        
        if not model_ids:
            # Get available models
            models = self.registry.list_models()
            if not models:
                print("❌ No models available for deployment")
                return []
            model_ids = [model.model_id for model in models[:2]]  # Use first 2 models
        
        deployments = []
        
        # Deploy models
        print("🚀 Deploying models...")
        for model_id in model_ids:
            model = self.registry.get_model(model_id)
            if not model:
                continue
                
            deployment_id = self.deployment.deploy_model(
                model_name=model.name,
                model_version=model.version,
                environment="staging",
                replicas=2,
                resources={"cpu": "200m", "memory": "512Mi"}
            )
            deployments.append(deployment_id)
            print(f"✅ Deployed {model.name} v{model.version} (Deployment: {deployment_id[:8]}...)")
        
        # Wait for deployments to complete
        print("\n⏳ Waiting for deployments to complete...")
        import time
        time.sleep(3)  # Wait for async deployment
        
        # Check deployment status
        print("\n📊 Deployment status:")
        for deployment_id in deployments:
            deployment = self.deployment.get_deployment(deployment_id)
            if deployment:
                print(f"  • {deployment.config.model_name}: {deployment.status.value}")
                
                # Get health status
                health = self.deployment.get_deployment_health(deployment_id)
                print(f"    Health: {health['status']}, Uptime: {health['uptime']}")
        
        # List all deployments
        print("\n📋 All deployments:")
        all_deployments = self.deployment.list_deployments()
        for dep in all_deployments:
            print(f"  • {dep.config.model_name} v{dep.config.model_version} ({dep.status.value})")
        
        # Get deployment statistics
        print("\n📊 Deployment statistics:")
        stats = self.deployment.get_deployment_stats()
        print(f"  • Total deployments: {stats['total_deployments']}")
        print(f"  • Active deployments: {stats['active_deployments']}")
        print(f"  • Status distribution: {stats['status_distribution']}")
        
        return deployments
    
    def demo_monitoring(self):
        """Demonstrate performance monitoring."""
        print("\n📊 PERFORMANCE MONITORING DEMONSTRATION")
        print("=" * 50)
        
        # Log system metrics
        print("📝 Logging system metrics...")
        metrics_to_log = [
            ("cpu_usage", 45.2, "percent"),
            ("memory_usage", 67.8, "percent"),
            ("disk_usage", 23.4, "percent"),
            ("request_count", 1250, "count"),
            ("response_time", 145.6, "milliseconds")
        ]
        
        for metric_name, value, unit in metrics_to_log:
            self.monitoring.log_system_metric(metric_name, value, unit)
            print(f"✅ Logged {metric_name}: {value} {unit}")
        
        # Log model performance metrics
        print("\n📝 Logging model performance metrics...")
        model_metrics = [
            ("chat-model", "1.0.0", "accuracy", 0.95),
            ("chat-model", "1.0.0", "latency_ms", 120),
            ("rag-model", "1.2.0", "recall", 0.88),
            ("rag-model", "1.2.0", "precision", 0.92),
            ("pricing-model", "2.0.0", "mae", 0.15)
        ]
        
        for model_name, version, metric_name, value in model_metrics:
            self.monitoring.log_model_performance(model_name, version, metric_name, value)
            print(f"✅ Logged {model_name} v{version} {metric_name}: {value}")
        
        # Get performance summary
        print("\n📊 Performance summary (last 24 hours):")
        summary = self.monitoring.get_performance_summary(hours=24)
        print(f"  • System metrics: {len(summary['system_metrics'])} types")
        print(f"  • Model performance: {len(summary['model_performance'])} models")
        
        # Get metric trends
        print("\n📈 Metric trends:")
        trends = self.monitoring.get_metric_trends("cpu_usage", hours=24)
        print(f"  • CPU usage trends: {len(trends)} data points")
        
        # Get recent metrics
        print("\n📋 Recent system metrics:")
        recent_metrics = self.monitoring.get_system_metrics(limit=5)
        for metric in recent_metrics:
            print(f"  • {metric.metric_name}: {metric.value} {metric.unit} ({metric.timestamp})")
    
    def demo_health_checking(self):
        """Demonstrate health checking."""
        print("\n🏥 HEALTH CHECKING DEMONSTRATION")
        print("=" * 50)
        
        # Run all health checks
        print("🔍 Running all health checks...")
        results = self.health.run_all_checks()
        
        print("\n📊 Health check results:")
        for check_name, result in results.items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }
            emoji = status_emoji.get(result.status.value, "❓")
            print(f"  {emoji} {check_name}: {result.message} ({result.response_time_ms:.1f}ms)")
        
        # Get overall health
        print("\n🏥 Overall system health:")
        overall = self.health.get_overall_health()
        print(f"  • Status: {overall['overall_status']}")
        print(f"  • Total checks: {overall['total_checks']}")
        print(f"  • Status distribution: {overall['status_counts']}")
        
        # Get failing checks
        print("\n⚠️  Failing checks:")
        failing = self.health.get_failing_checks(hours=1)
        if failing:
            for check in failing:
                print(f"  • {check.check_name}: {check.message}")
        else:
            print("  ✅ No failing checks found")
        
        # Get health history
        print("\n📈 Health check history:")
        history = self.health.get_health_history(limit=5)
        for check in history:
            print(f"  • {check.check_name}: {check.status.value} ({check.timestamp})")
    
    def demo_integration(self):
        """Demonstrate MLOps integration workflow."""
        print("\n🔗 MLOPS INTEGRATION WORKFLOW DEMONSTRATION")
        print("=" * 50)
        
        print("🔄 Simulating complete MLOps workflow...")
        
        # 1. Model Registration
        print("\n1️⃣ Model Registration:")
        model_id = self.registry.register_model(
            model_name="integration-test-model",
            version="1.0.0",
            model_type="test",
            file_path="./models/test_model.pkl",
            performance_metrics={"accuracy": 0.90, "latency_ms": 100},
            tags=["test", "integration"],
            description="Test model for integration workflow"
        )
        print(f"✅ Model registered: {model_id[:8]}...")
        
        # 2. Model Deployment
        print("\n2️⃣ Model Deployment:")
        deployment_id = self.deployment.deploy_model(
            model_name="integration-test-model",
            model_version="1.0.0",
            environment="staging"
        )
        print(f"✅ Model deployed: {deployment_id[:8]}...")
        
        # 3. Performance Monitoring
        print("\n3️⃣ Performance Monitoring:")
        self.monitoring.log_model_performance(
            "integration-test-model", "1.0.0", "accuracy", 0.92
        )
        print("✅ Performance metrics logged")
        
        # 4. Health Checking
        print("\n4️⃣ Health Checking:")
        health_result = self.health.run_check("cpu_usage")
        print(f"✅ Health check completed: {health_result.status.value}")
        
        # 5. Model Update
        print("\n5️⃣ Model Performance Update:")
        success = self.registry.update_model_performance(
            model_id, {"accuracy": 0.94, "latency_ms": 95}
        )
        print(f"✅ Model performance updated: {'Success' if success else 'Failed'}")
        
        print("\n🎉 Complete MLOps workflow demonstrated successfully!")
    
    def run_demo(self, component="all", interactive=False):
        """Run MLOps demonstration."""
        print("🤖 KcartBot MLOps Demonstration")
        print("=" * 50)
        print(f"Component: {component}")
        print(f"Interactive: {interactive}")
        print(f"Timestamp: {datetime.now()}")
        
        try:
            if component == "registry" or component == "all":
                model_ids = self.demo_model_registry()
            
            if component == "deployment" or component == "all":
                deployments = self.demo_deployment(model_ids if 'model_ids' in locals() else None)
            
            if component == "monitoring" or component == "all":
                self.demo_monitoring()
            
            if component == "health" or component == "all":
                self.demo_health_checking()
            
            if component == "integration" or component == "all":
                self.demo_integration()
            
            print("\n✅ MLOps demonstration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during demonstration: {e}")
            import traceback
            traceback.print_exc()
    
    def interactive_mode(self):
        """Run interactive MLOps demonstration."""
        print("\n🎮 INTERACTIVE MLOPS MODE")
        print("=" * 30)
        
        while True:
            print("\nAvailable commands:")
            print("1. registry  - Model registry operations")
            print("2. deployment - Deployment management")
            print("3. monitoring - Performance monitoring")
            print("4. health    - Health checking")
            print("5. integration - Complete workflow")
            print("6. stats     - Show all statistics")
            print("7. quit      - Exit")
            
            choice = input("\nEnter command (1-7): ").strip()
            
            if choice == "1":
                self.demo_model_registry()
            elif choice == "2":
                self.demo_deployment()
            elif choice == "3":
                self.demo_monitoring()
            elif choice == "4":
                self.demo_health_checking()
            elif choice == "5":
                self.demo_integration()
            elif choice == "6":
                self.show_all_stats()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_all_stats(self):
        """Show comprehensive statistics from all components."""
        print("\n📊 COMPREHENSIVE MLOPS STATISTICS")
        print("=" * 50)
        
        # Model Registry Stats
        print("\n🏗️  Model Registry:")
        registry_stats = self.registry.get_model_stats()
        print(f"  • Total models: {registry_stats['total_models']}")
        print(f"  • Active models: {registry_stats['active_models']}")
        print(f"  • Models by type: {registry_stats['models_by_type']}")
        
        # Deployment Stats
        print("\n🚀 Deployments:")
        deployment_stats = self.deployment.get_deployment_stats()
        print(f"  • Total deployments: {deployment_stats['total_deployments']}")
        print(f"  • Active deployments: {deployment_stats['active_deployments']}")
        print(f"  • Status distribution: {deployment_stats['status_distribution']}")
        
        # Health Stats
        print("\n🏥 Health Status:")
        health_overall = self.health.get_overall_health()
        print(f"  • Overall status: {health_overall['overall_status']}")
        print(f"  • Total checks: {health_overall['total_checks']}")
        print(f"  • Status counts: {health_overall['status_counts']}")
        
        # Performance Stats
        print("\n📊 Performance:")
        perf_summary = self.monitoring.get_performance_summary(hours=24)
        print(f"  • System metrics: {len(perf_summary['system_metrics'])} types")
        print(f"  • Model performance: {len(perf_summary['model_performance'])} models")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="KcartBot MLOps Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--component",
        choices=["registry", "deployment", "monitoring", "health", "integration", "all"],
        default="all",
        help="MLOps component to demonstrate (default: all)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = MLOpsDemo()
    
    if args.interactive:
        demo.interactive_mode()
    else:
        demo.run_demo(args.component, args.interactive)


if __name__ == "__main__":
    main()
