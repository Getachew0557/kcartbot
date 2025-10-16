"""Demo script to test KcartBot functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.chat_service import GeminiChatService
from src.services.rag_service import RAGService
from src.mcp.server import MCPServer


async def demo_customer_flow():
    """Demonstrate customer flow."""
    print("=== CUSTOMER FLOW DEMO ===\n")
    
    chat_service = GeminiChatService()
    
    # Simulate customer conversation
    messages = [
        "Hello, I want to register as a customer",
        "My name is Alem, phone +251911234567",
        "Addis Ababa",
        "I want to order some tomatoes",
        "How should I store tomatoes?",
        "I want 5kg of red onions and 2 liters of milk",
        "Tomorrow"
    ]
    
    session_data = {}
    
    for message in messages:
        print(f"User: {message}")
        
        try:
            result = await chat_service.process_message(message, session_data)
            print(f"Bot: {result['response']}")
            print(f"Language: {result['language']}")
            session_data = result['session_data']
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 50)


async def demo_supplier_flow():
    """Demonstrate supplier flow."""
    print("\n=== SUPPLIER FLOW DEMO ===\n")
    
    chat_service = GeminiChatService()
    
    # Simulate supplier conversation
    messages = [
        "I'm a supplier, I want to register",
        "I'm Lema, phone +251922345678",
        "I want to add tomatoes",
        "100kg",
        "This Friday",
        "What do you suggest for pricing?",
        "55 ETB per kg"
    ]
    
    session_data = {}
    
    for message in messages:
        print(f"User: {message}")
        
        try:
            result = await chat_service.process_message(message, session_data)
            print(f"Bot: {result['response']}")
            print(f"Language: {result['language']}")
            session_data = result['session_data']
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 50)


async def demo_rag_system():
    """Demonstrate RAG system."""
    print("\n=== RAG SYSTEM DEMO ===\n")
    
    try:
        rag_service = RAGService()
        
        # Test knowledge search
        queries = [
            "storage tips for tomatoes",
            "nutritional information about avocados",
            "recipes using Ayib"
        ]
        
        for query in queries:
            print(f"Query: {query}")
            results = rag_service.search_knowledge(query, limit=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['content']}")
                    print(f"   Type: {result['metadata']['knowledge_type']}")
            else:
                print("No results found")
            print("-" * 50)
            
    except Exception as e:
        print(f"RAG Demo Error: {e}")


async def demo_mcp_tools():
    """Demonstrate MCP tools."""
    print("\n=== MCP TOOLS DEMO ===\n")
    
    mcp_server = MCPServer()
    
    # Get available tools
    tools = mcp_server.get_tools_schema()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nTesting tool execution...")
    
    # Test product search
    try:
        result = await mcp_server.execute_tool("search_products", {
            "query": "tomato",
            "available_only": True
        })
        print(f"Product search result: {result.get('success', False)}")
        if result.get('success'):
            products = result.get('products', [])
            print(f"Found {len(products)} products")
    except Exception as e:
        print(f"MCP Demo Error: {e}")


async def main():
    """Main demo function."""
    print("🚀 KcartBot Demo Starting...\n")
    
    try:
        # Run demos
        await demo_customer_flow()
        await demo_supplier_flow()
        await demo_rag_system()
        await demo_mcp_tools()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure to run 'python data/generate_data.py' first to create the database")


if __name__ == "__main__":
    asyncio.run(main())

