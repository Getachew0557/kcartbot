"""FastAPI application for KcartBot."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

from config import settings
from database.connection import init_database, get_db
from services.chat_service import GeminiChatService
from services.rag_service import RAGService
from mcp.server import MCPServer

# Initialize FastAPI app
app = FastAPI(
    title="KcartBot API",
    description="Advanced AI Agri-Commerce Assistant for Ethiopia",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chat_service = GeminiChatService()
rag_service = RAGService()
mcp_server = MCPServer()


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_data: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    language: str
    session_data: Dict[str, Any]
    tools_used: Optional[List[Dict]] = None
    error: Optional[str] = None


class UserRegistration(BaseModel):
    name: str
    phone: str
    user_type: str  # "customer" or "supplier"
    location: Optional[str] = None


class ProductSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    available_only: bool = True


class OrderRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: float
    delivery_date: Optional[str] = None
    delivery_location: Optional[str] = None


class ProductAddition(BaseModel):
    supplier_id: str
    name: str
    category: str
    unit: str = "kg"
    quantity: float
    price: float
    expiry_date: Optional[str] = None


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()
    print("KcartBot API started successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to KcartBot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "KcartBot API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint."""
    try:
        result = await chat_service.process_message(
            message.message, 
            message.session_data
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/welcome/{language}")
async def get_welcome_message(language: str = "en"):
    """Get welcome message in specified language."""
    return {
        "message": chat_service.get_welcome_message(language),
        "language": language
    }


@app.post("/users/register")
async def register_user(user: UserRegistration):
    """Register a new user."""
    try:
        result = await mcp_server.execute_tool("register_user", user.dict())
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Registration failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/products/search")
async def search_products(search: ProductSearch):
    """Search for products."""
    try:
        result = await mcp_server.execute_tool("search_products", search.dict())
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Search failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}")
async def get_product_info(product_id: str, include_pricing: bool = False):
    """Get detailed product information."""
    try:
        result = await mcp_server.execute_tool(
            "get_product_info", 
            {"product_id": product_id, "include_pricing": include_pricing}
        )
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Product not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders")
async def create_order(order: OrderRequest):
    """Create a new order."""
    try:
        result = await mcp_server.execute_tool("create_order", order.dict())
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Order creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}/pricing-insights")
async def get_pricing_insights(product_id: str, days_back: int = 30):
    """Get pricing insights for a product."""
    try:
        result = await mcp_server.execute_tool(
            "get_pricing_insights",
            {"product_id": product_id, "days_back": days_back}
        )
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Product not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suppliers/products")
async def add_product(product: ProductAddition):
    """Add a new product (supplier only)."""
    try:
        result = await mcp_server.execute_tool("add_product", product.dict())
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Product addition failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/suppliers/{supplier_id}/orders")
async def get_supplier_orders(
    supplier_id: str, 
    status: Optional[str] = None, 
    days_ahead: Optional[int] = None
):
    """Get orders for a supplier."""
    try:
        params = {"supplier_id": supplier_id}
        if status:
            params["status"] = status
        if days_ahead:
            params["days_ahead"] = days_ahead
            
        result = await mcp_server.execute_tool("get_supplier_orders", params)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Supplier not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/search")
async def search_knowledge(
    query: str,
    product_id: Optional[str] = None,
    knowledge_type: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 5
):
    """Search product knowledge base."""
    try:
        knowledge_items = rag_service.search_knowledge(
            query=query,
            product_id=product_id,
            knowledge_type=knowledge_type,
            language=language,
            limit=limit
        )
        return {
            "success": True,
            "knowledge": knowledge_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/products/{product_id}")
async def get_product_knowledge(product_id: str, knowledge_type: Optional[str] = None):
    """Get all knowledge for a specific product."""
    try:
        knowledge_items = rag_service.get_product_knowledge(product_id, knowledge_type)
        return {
            "success": True,
            "knowledge": knowledge_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics."""
    try:
        stats = rag_service.get_knowledge_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def get_available_tools():
    """Get available MCP tools."""
    return {
        "success": True,
        "tools": mcp_server.get_tools_schema()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
