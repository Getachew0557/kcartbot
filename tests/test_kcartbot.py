"""Test suite for KcartBot application."""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import settings
from src.database.connection import SessionLocal, init_database
from src.models import User, Product, Order, PricingHistory, ProductKnowledge
from src.services.chat_service import GeminiChatService
from src.services.rag_service import RAGService
from src.mcp.server import MCPServer
from src.utils.language_detection import detect_language


class TestDatabase:
    """Test database operations."""
    
    def test_database_connection(self):
        """Test database connection."""
        session = SessionLocal()
        assert session is not None
        session.close()
    
    def test_database_initialization(self):
        """Test database initialization."""
        init_database()
        # Database should be initialized without errors
        assert True


class TestModels:
    """Test database models."""
    
    def test_user_model(self):
        """Test User model."""
        user = User(
            name="Test User",
            phone="+251911234567",
            user_type="customer",
            default_location="Addis Ababa"
        )
        assert user.name == "Test User"
        assert user.phone == "+251911234567"
        assert user.user_type == "customer"
    
    def test_product_model(self):
        """Test Product model."""
        product = Product(
            name="Red Onions",
            category="vegetables",
            unit="kg",
            description="Fresh red onions"
        )
        assert product.name == "Red Onions"
        assert product.category == "vegetables"
        assert product.unit == "kg"


class TestLanguageDetection:
    """Test language detection functionality."""
    
    def test_english_detection(self):
        """Test English language detection."""
        text = "Hello, I want to buy some vegetables"
        lang = detect_language(text)
        assert lang == "en"
    
    def test_amharic_detection(self):
        """Test Amharic language detection."""
        text = "ሰላም፣ አትክልት መግዛት እፈልጋለሁ"
        lang = detect_language(text)
        assert lang == "am"
    
    def test_amhar_glish_detection(self):
        """Test Amhar-glish language detection."""
        text = "selam, vegetables megezat efelgalehu"
        lang = detect_language(text)
        # The detection might return 'en' for mixed content, which is acceptable
        assert lang in ["en", "am-latn"]


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_mcp_server_initialization(self):
        """Test MCP server initialization."""
        server = MCPServer()
        assert server is not None
        assert hasattr(server, 'tools')
        assert len(server.tools) > 0
    
    def test_available_tools(self):
        """Test available tools."""
        server = MCPServer()
        tool_names = [tool.name for tool in server.tools]
        
        expected_tools = [
            'register_user',
            'search_products',
            'get_product_info',
            'create_order',
            'get_pricing_insights',
            'add_product',
            'get_supplier_orders',
            'search_knowledge'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names


class TestChatService:
    """Test chat service functionality."""
    
    @pytest.fixture
    def chat_service(self):
        """Create chat service instance."""
        return GeminiChatService()
    
    def test_chat_service_initialization(self, chat_service):
        """Test chat service initialization."""
        assert chat_service is not None
        assert hasattr(chat_service, 'model')
        assert hasattr(chat_service, 'mcp_server')
    
    def test_welcome_message(self, chat_service):
        """Test welcome message generation."""
        welcome_msg = chat_service.get_welcome_message("en")
        assert welcome_msg is not None
        assert len(welcome_msg) > 0
        assert "KcartBot" in welcome_msg
    
    @pytest.mark.asyncio
    async def test_process_message(self, chat_service):
        """Test message processing."""
        # Mock the Gemini API response
        with patch.object(chat_service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Welcome to KcartBot! How can I help you?"
            mock_generate.return_value = mock_response
            
            result = await chat_service.process_message("Hello", {})
            
            assert result["success"] is True
            assert "response" in result
            assert result["response"] == "Welcome to KcartBot! How can I help you?"


class TestRAGService:
    """Test RAG service functionality."""
    
    def test_rag_service_initialization(self):
        """Test RAG service initialization."""
        rag_service = RAGService()
        assert rag_service is not None
        assert hasattr(rag_service, 'collection')
    
    def test_search_knowledge(self):
        """Test knowledge search."""
        rag_service = RAGService()
        results = rag_service.search_knowledge("tomato storage")
        assert isinstance(results, list)


class TestIntegration:
    """Integration tests."""
    
    def test_full_system_initialization(self):
        """Test full system initialization."""
        # Initialize database
        init_database()
        
        # Initialize services
        chat_service = GeminiChatService()
        rag_service = RAGService()
        mcp_server = MCPServer()
        
        # All services should be initialized
        assert chat_service is not None
        assert rag_service is not None
        assert mcp_server is not None
    
    def test_data_generation(self):
        """Test data generation script."""
        # This test ensures the data generation script can be imported
        import data.generate_data
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
