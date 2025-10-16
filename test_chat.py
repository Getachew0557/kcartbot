"""Test script to verify chat functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_chat_service():
    """Test the chat service directly."""
    print("🧪 Testing KcartBot Chat Service...")
    
    try:
        from src.services.chat_service import GeminiChatService
        
        # Initialize chat service
        chat_service = GeminiChatService()
        print("✅ Chat service initialized successfully")
        
        # Test welcome message
        welcome_msg = chat_service.get_welcome_message("en")
        print(f"✅ Welcome message: {welcome_msg}")
        
        # Test language detection
        lang = chat_service.detect_language("I want to register as a customer")
        print(f"✅ Language detected: {lang}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat service: {e}")
        return False

def test_mcp_tools():
    """Test MCP tools directly."""
    print("\n🔧 Testing MCP Tools...")
    
    try:
        from src.mcp.server import MCPServer
        
        # Initialize MCP server
        mcp_server = MCPServer()
        print("✅ MCP server initialized successfully")
        
        # Test tools schema
        tools = mcp_server.get_tools_schema()
        print(f"✅ Available tools: {len(tools)}")
        
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        return False

async def test_full_conversation():
    """Test a full conversation."""
    print("\n💬 Testing Full Conversation...")
    
    try:
        from src.services.chat_service import GeminiChatService
        
        chat_service = GeminiChatService()
        
        # Test message
        message = "I want to register as a customer"
        print(f"📤 Sending: {message}")
        
        result = await chat_service.process_message(message)
        
        if result["success"]:
            print(f"📥 Response: {result['response']}")
            print(f"🌍 Language: {result['language']}")
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in conversation test: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 KcartBot Chat Service Test")
    print("=" * 50)
    
    # Test chat service
    chat_ok = test_chat_service()
    
    # Test MCP tools
    mcp_ok = test_mcp_tools()
    
    # Test full conversation
    if chat_ok and mcp_ok:
        print("\n🔄 Testing full conversation...")
        conversation_ok = asyncio.run(test_full_conversation())
        
        if conversation_ok:
            print("\n✅ All tests passed! Chat functionality is working.")
        else:
            print("\n❌ Conversation test failed.")
    else:
        print("\n❌ Basic tests failed. Cannot test conversation.")

if __name__ == "__main__":
    main()
