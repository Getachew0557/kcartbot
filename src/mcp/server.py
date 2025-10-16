"""MCP (Model Context Protocol) server implementation for KcartBot."""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import SessionLocal
from models import User, Product, Order, PricingHistory, ProductKnowledge


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPServer:
    """MCP Server for KcartBot tool-calling framework."""
    
    def __init__(self):
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools."""
        return [
            MCPTool(
                name="register_user",
                description="Register a new user (customer or supplier)",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "User's name"},
                        "phone": {"type": "string", "description": "User's phone number"},
                        "user_type": {"type": "string", "enum": ["customer", "supplier"], "description": "Type of user"},
                        "location": {"type": "string", "description": "Default location"}
                    },
                    "required": ["name", "phone", "user_type"]
                }
            ),
            MCPTool(
                name="search_products",
                description="Search for products by name or category",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "category": {"type": "string", "enum": ["horticulture", "dairy"], "description": "Product category"},
                        "available_only": {"type": "boolean", "description": "Only show available products"}
                    }
                }
            ),
            MCPTool(
                name="get_product_info",
                description="Get detailed information about a specific product",
                parameters={
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "Product ID"},
                        "include_pricing": {"type": "boolean", "description": "Include pricing information"}
                    },
                    "required": ["product_id"]
                }
            ),
            MCPTool(
                name="create_order",
                description="Create a new order",
                parameters={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "product_id": {"type": "string", "description": "Product ID"},
                        "quantity": {"type": "number", "description": "Quantity to order"},
                        "delivery_date": {"type": "string", "description": "Preferred delivery date"},
                        "delivery_location": {"type": "string", "description": "Delivery location"}
                    },
                    "required": ["user_id", "product_id", "quantity"]
                }
            ),
            MCPTool(
                name="get_pricing_insights",
                description="Get pricing insights and competitor analysis for a product",
                parameters={
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "Product ID"},
                        "days_back": {"type": "integer", "description": "Number of days to look back"}
                    },
                    "required": ["product_id"]
                }
            ),
            MCPTool(
                name="add_product",
                description="Add a new product (supplier only)",
                parameters={
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "string", "description": "Supplier ID"},
                        "name": {"type": "string", "description": "Product name"},
                        "category": {"type": "string", "enum": ["horticulture", "dairy"], "description": "Product category"},
                        "unit": {"type": "string", "description": "Unit of measurement"},
                        "quantity": {"type": "number", "description": "Available quantity"},
                        "price": {"type": "number", "description": "Price per unit"},
                        "expiry_date": {"type": "string", "description": "Expiry date"}
                    },
                    "required": ["supplier_id", "name", "category", "quantity", "price"]
                }
            ),
            MCPTool(
                name="get_supplier_orders",
                description="Get orders for a supplier",
                parameters={
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "string", "description": "Supplier ID"},
                        "status": {"type": "string", "enum": ["pending", "confirmed", "delivered"], "description": "Order status"},
                        "days_ahead": {"type": "integer", "description": "Days ahead to look"}
                    },
                    "required": ["supplier_id"]
                }
            ),
            MCPTool(
                name="search_knowledge",
                description="Search product knowledge base using RAG",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Knowledge search query"},
                        "product_id": {"type": "string", "description": "Specific product ID"},
                        "knowledge_type": {"type": "string", "enum": ["storage", "nutrition", "recipe", "seasonal"], "description": "Type of knowledge"}
                    },
                    "required": ["query"]
                }
            )
        ]
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get tools schema for LLM."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool."""
        db = SessionLocal()
        try:
            if tool_name == "register_user":
                return await self._register_user(db, parameters)
            elif tool_name == "search_products":
                return await self._search_products(db, parameters)
            elif tool_name == "get_product_info":
                return await self._get_product_info(db, parameters)
            elif tool_name == "create_order":
                return await self._create_order(db, parameters)
            elif tool_name == "get_pricing_insights":
                return await self._get_pricing_insights(db, parameters)
            elif tool_name == "add_product":
                return await self._add_product(db, parameters)
            elif tool_name == "get_supplier_orders":
                return await self._get_supplier_orders(db, parameters)
            elif tool_name == "search_knowledge":
                return await self._search_knowledge(db, parameters)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
    
    async def _register_user(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user."""
        user = User(
            name=params["name"],
            phone=params["phone"],
            user_type=params["user_type"],
            default_location=params.get("location")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "user_id": user.id,
            "message": f"User {user.name} registered successfully as {user.user_type}"
        }
    
    async def _search_products(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for products."""
        query = db.query(Product).filter(Product.is_active == True)
        
        if "query" in params:
            search_term = params["query"].lower()
            query = query.filter(
                (Product.name.ilike(f"%{search_term}%")) |
                (Product.name_amharic.ilike(f"%{search_term}%"))
            )
        
        if "category" in params:
            query = query.filter(Product.category == params["category"])
        
        if params.get("available_only", False):
            query = query.filter(Product.quantity_available > 0)
        
        products = query.limit(20).all()
        
        return {
            "success": True,
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "name_amharic": p.name_amharic,
                    "category": p.category,
                    "unit": p.unit,
                    "current_price": p.current_price,
                    "quantity_available": p.quantity_available
                }
                for p in products
            ]
        }
    
    async def _get_product_info(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed product information."""
        product = db.query(Product).filter(Product.id == params["product_id"]).first()
        
        if not product:
            return {"error": "Product not found"}
        
        result = {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "name_amharic": product.name_amharic,
                "category": product.category,
                "unit": product.unit,
                "description": product.description,
                "current_price": product.current_price,
                "quantity_available": product.quantity_available,
                "expiry_date": product.expiry_date.isoformat() if product.expiry_date else None
            }
        }
        
        if params.get("include_pricing", False):
            # Get recent pricing history
            pricing = db.query(PricingHistory).filter(
                PricingHistory.product_id == product.id
            ).order_by(PricingHistory.date.desc()).limit(10).all()
            
            result["pricing_history"] = [
                {
                    "price": p.price,
                    "source": p.source_market_type,
                    "location": p.location_detail,
                    "date": p.date.isoformat()
                }
                for p in pricing
            ]
        
        return result
    
    async def _create_order(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order."""
        product = db.query(Product).filter(Product.id == params["product_id"]).first()
        
        if not product:
            return {"error": "Product not found"}
        
        if product.quantity_available < params["quantity"]:
            return {"error": f"Insufficient stock. Available: {product.quantity_available} {product.unit}"}
        
        # Calculate total amount
        total_amount = params["quantity"] * product.current_price
        
        order = Order(
            user_id=params["user_id"],
            product_id=params["product_id"],
            quantity_ordered=params["quantity"],
            unit_price=product.current_price,
            total_amount=total_amount,
            delivery_date=datetime.fromisoformat(params["delivery_date"]) if "delivery_date" in params else None,
            delivery_location=params.get("delivery_location"),
            payment_method="COD",
            status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return {
            "success": True,
            "order_id": order.id,
            "total_amount": total_amount,
            "message": "Order created successfully. Payment is Cash on Delivery."
        }
    
    async def _get_pricing_insights(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing insights and competitor analysis."""
        product = db.query(Product).filter(Product.id == params["product_id"]).first()
        
        if not product:
            return {"error": "Product not found"}
        
        days_back = params.get("days_back", 30)
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get pricing history
        pricing_history = db.query(PricingHistory).filter(
            PricingHistory.product_id == product.id,
            PricingHistory.date >= start_date
        ).all()
        
        # Calculate insights
        insights = {
            "product_name": product.name,
            "current_price": product.current_price,
            "competitor_analysis": {},
            "recommendations": []
        }
        
        # Group by market type
        market_prices = {}
        for p in pricing_history:
            if p.source_market_type not in market_prices:
                market_prices[p.source_market_type] = []
            market_prices[p.source_market_type].append(p.price)
        
        # Calculate averages
        for market_type, prices in market_prices.items():
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                insights["competitor_analysis"][market_type] = {
                    "average_price": round(avg_price, 2),
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2),
                    "sample_size": len(prices)
                }
        
        # Generate recommendations
        if "local_shop" in market_prices and "supermarket" in market_prices:
            local_avg = insights["competitor_analysis"]["local_shop"]["average_price"]
            super_avg = insights["competitor_analysis"]["supermarket"]["average_price"]
            
            if product.current_price > super_avg:
                insights["recommendations"].append(
                    f"Consider reducing price. Current price ({product.current_price}) is above supermarket average ({super_avg})"
                )
            elif product.current_price < local_avg:
                insights["recommendations"].append(
                    f"Good pricing! Current price ({product.current_price}) is competitive with local shops ({local_avg})"
                )
        
        return {"success": True, "insights": insights}
    
    async def _add_product(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new product (supplier only)."""
        supplier = db.query(User).filter(
            User.id == params["supplier_id"],
            User.user_type == "supplier"
        ).first()
        
        if not supplier:
            return {"error": "Supplier not found"}
        
        product = Product(
            name=params["name"],
            category=params["category"],
            unit=params.get("unit", "kg"),
            supplier_id=params["supplier_id"],
            current_price=params["price"],
            quantity_available=params["quantity"],
            expiry_date=datetime.fromisoformat(params["expiry_date"]) if "expiry_date" in params else None
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return {
            "success": True,
            "product_id": product.id,
            "message": f"Product {product.name} added successfully"
        }
    
    async def _get_supplier_orders(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get orders for a supplier."""
        supplier_id = params["supplier_id"]
        
        # Get supplier's products
        products = db.query(Product).filter(Product.supplier_id == supplier_id).all()
        product_ids = [p.id for p in products]
        
        if not product_ids:
            return {"success": True, "orders": []}
        
        # Query orders
        query = db.query(Order).filter(Order.product_id.in_(product_ids))
        
        if "status" in params:
            query = query.filter(Order.status == params["status"])
        
        if "days_ahead" in params:
            end_date = datetime.utcnow() + timedelta(days=params["days_ahead"])
            query = query.filter(Order.delivery_date <= end_date)
        
        orders = query.order_by(Order.created_at.desc()).limit(50).all()
        
        return {
            "success": True,
            "orders": [
                {
                    "id": o.id,
                    "product_name": o.product.name,
                    "quantity": o.quantity_ordered,
                    "total_amount": o.total_amount,
                    "status": o.status,
                    "delivery_date": o.delivery_date.isoformat() if o.delivery_date else None,
                    "customer_name": o.user.name
                }
                for o in orders
            ]
        }
    
    async def _search_knowledge(self, db, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search product knowledge base."""
        query = db.query(ProductKnowledge)
        
        if "product_id" in params:
            query = query.filter(ProductKnowledge.product_id == params["product_id"])
        
        if "knowledge_type" in params:
            query = query.filter(ProductKnowledge.knowledge_type == params["knowledge_type"])
        
        # Simple text search (in production, use vector search)
        search_term = params["query"].lower()
        knowledge_items = query.filter(
            ProductKnowledge.content.ilike(f"%{search_term}%")
        ).limit(10).all()
        
        return {
            "success": True,
            "knowledge": [
                {
                    "id": k.id,
                    "product_id": k.product_id,
                    "type": k.knowledge_type,
                    "content": k.content,
                    "language": k.language
                }
                for k in knowledge_items
            ]
        }
