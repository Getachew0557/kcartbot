"""Test files for KcartBot."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.services.chat_service import GeminiChatService
from src.services.rag_service import RAGService
from src.mcp.server import MCPServer
from src.utils.language_detection import LanguageDetector
from src.utils.helpers import validate_phone, format_currency, calculate_order_total


class TestLanguageDetector:
    """Test language detection functionality."""
    
    def test_detect_english(self):
        detector = LanguageDetector()
        assert detector.detect_language("Hello, I want to order some tomatoes") == "en"
    
    def test_detect_amharic(self):
        detector = LanguageDetector()
        assert detector.detect_language("ሰላም፣ ቲማቲም እፈልጋለሁ") == "am"
    
    def test_detect_amhar_glish(self):
        detector = LanguageDetector()
        assert detector.detect_language("Salam, timatim efelgalew") == "am-latn"


class TestHelpers:
    """Test helper functions."""
    
    def test_validate_phone(self):
        assert validate_phone("+251911234567") == True
        assert validate_phone("0911234567") == True
        assert validate_phone("251911234567") == True
        assert validate_phone("1234567890") == False
    
    def test_format_currency(self):
        assert format_currency(150.50) == "150.50 ETB"
        assert format_currency(0) == "0.00 ETB"
    
    def test_calculate_order_total(self):
        assert calculate_order_total(5.0, 20.0) == 100.0
        assert calculate_order_total(2.5, 15.0) == 37.5


class TestMCPServer:
    """Test MCP server functionality."""
    
    @pytest.fixture
    def mcp_server(self):
        return MCPServer()
    
    def test_get_tools_schema(self, mcp_server):
        tools = mcp_server.get_tools_schema()
        assert len(tools) > 0
        assert any(tool["name"] == "register_user" for tool in tools)
        assert any(tool["name"] == "search_products" for tool in tools)
    
    @pytest.mark.asyncio
    async def test_register_user(self, mcp_server):
        # Mock database session
        with patch('src.mcp.server.SessionLocal') as mock_session:
            mock_db = Mock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            result = await mcp_server.execute_tool("register_user", {
                "name": "Test User",
                "phone": "+251911234567",
                "user_type": "customer"
            })
            
            assert result["success"] == True
            assert "user_id" in result


class TestRAGService:
    """Test RAG service functionality."""
    
    @pytest.fixture
    def rag_service(self):
        with patch('src.services.rag_service.chromadb.PersistentClient'):
            with patch('src.services.rag_service.SentenceTransformer'):
                return RAGService()
    
    def test_search_knowledge(self, rag_service):
        with patch.object(rag_service.collection, 'query') as mock_query:
            mock_query.return_value = {
                'documents': [['Test knowledge content']],
                'metadatas': [[{'product_id': 'test-id', 'knowledge_type': 'storage'}]],
                'distances': [[0.1]]
            }
            
            results = rag_service.search_knowledge("storage tips")
            assert len(results) > 0
            assert results[0]["content"] == "Test knowledge content"


class TestChatService:
    """Test chat service functionality."""
    
    @pytest.fixture
    def chat_service(self):
        with patch('src.services.chat_service.genai.configure'):
            with patch('src.services.chat_service.genai.GenerativeModel'):
                return GeminiChatService()
    
    def test_get_welcome_message(self, chat_service):
        en_msg = chat_service.get_welcome_message("en")
        am_msg = chat_service.get_welcome_message("am")
        
        assert "Welcome" in en_msg
        assert "እንኳን" in am_msg
    
    @pytest.mark.asyncio
    async def test_process_message(self, chat_service):
        with patch.object(chat_service, '_generate_response_with_tools') as mock_generate:
            mock_generate.return_value = {
                "content": "Test response",
                "tools_used": []
            }
            
            result = await chat_service.process_message("Hello")
            
            assert result["success"] == True
            assert result["response"] == "Test response"


# Integration tests
class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_customer_registration_flow(self):
        """Test complete customer registration flow."""
        mcp_server = MCPServer()
        
        with patch('src.mcp.server.SessionLocal') as mock_session:
            mock_db = Mock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Register customer
            result = await mcp_server.execute_tool("register_user", {
                "name": "Test Customer",
                "phone": "+251911234567",
                "user_type": "customer",
                "location": "Addis Ababa"
            })
            
            assert result["success"] == True
            assert "customer" in result["message"]
    
    @pytest.mark.asyncio
    async def test_supplier_product_addition_flow(self):
        """Test supplier product addition flow."""
        mcp_server = MCPServer()
        
        with patch('src.mcp.server.SessionLocal') as mock_session:
            mock_db = Mock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Add product
            result = await mcp_server.execute_tool("add_product", {
                "supplier_id": "test-supplier-id",
                "name": "Fresh Tomatoes",
                "category": "horticulture",
                "quantity": 50,
                "price": 25.0
            })
            
            assert result["success"] == True
            assert "Tomatoes" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__])

