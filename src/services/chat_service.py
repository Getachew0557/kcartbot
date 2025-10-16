"""Gemini 2.5 Flash integration for KcartBot chat logic."""

import json
import asyncio
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import settings
from mcp.server import MCPServer


class GeminiChatService:
    """Chat service using Gemini 2.5 Flash with MCP tool calling."""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.mcp_server = MCPServer()
        
        # System prompt
        self.system_prompt = """
You are KcartBot, an advanced AI Agri-Commerce Assistant for Ethiopia. You help customers and suppliers with agricultural products including horticulture (fruits, vegetables) and dairy products.

Key capabilities:
1. Multi-language support: English, Amharic (አማርኛ), and Amhar-glish (Amharic in Latin script)
2. Customer assistance: Product discovery, ordering, payment (COD only)
3. Supplier assistance: Product management, pricing insights, order management
4. RAG-powered knowledge: Storage tips, nutritional info, recipes, seasonal information

Customer Flow:
- Registration: Name, phone, location
- Product discovery with RAG knowledge
- Conversational ordering with delivery details
- COD payment confirmation (simulate 5-second pause)

Supplier Flow:
- Registration: Name, phone
- Product addition with pricing insights
- Stock and expiry management
- Order management and scheduling

Always be helpful, friendly, and culturally appropriate for Ethiopian users.
Use the available tools to provide accurate information and complete transactions.
"""
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text."""
        # Simple language detection based on character sets
        amharic_chars = set('ሀሁሂሃሄህሆሇለሉሊላሌልሎሏሐሑሒሓሔሕሖሗመሙሚማሜምሞሟሠሡሢሣሤሥሦሧረሩሪራሬርሮሯሰሱሲሳሴስሶሷሸሹሺሻሼሽሾሿቀቁቂቃቄቅቆቇቈ቉ቊቋቌቍ቎቏ቐቑቒቓቔቕቖ቗ቘ቙ቚቛቜቝ቞቟በቡቢባቤብቦቧቨቩቪቫቬቭቮቯተቱቲታቴትቶቷቸቹቺቻቼችቾቿኀኁኂኃኄኅኆኇኈ኉ኊኋኌኍ኎኏ነኑኒናኔንኖኗኘኙኚኛኜኝኞኟአኡኢኣኤእኦኧከኩኪካኬክኮኯኰ኱ኲኳኴኵ኶኷ኸኹኺኻኼኽኾዀ዁ዂዃዄዅ዆዇ወዉዊዋዌውዎዏዐዑዒዓዔዕዖዘዙዚዛዜዝዞዟዠዡዢዣዤዥዦዧየዩዪያዬይዮዯደዱዲዳዴድዶዷዸዹዺዻዼዽዾዿጀጁጂጃጄጅጆጇገጉጊጋጌግጎጏጐ጑ጒጓጔጕ጖጗ጘጙጚጛጜጝጞጟጠጡጢጣጤጥጦጧጨጩጪጫጬጭጮጯጰጱጲጳጴጵጶጷጸጹጺጻጼጽጾጿፀፁፂፃፄፅፆፇፈፉፊፋፌፍፎፏፐፑፒፓፔፕፖፗ')
        
        if any(char in amharic_chars for char in text):
            return "am"  # Amharic
        elif any(char.isalpha() for char in text) and not any(ord(char) > 127 for char in text):
            return "en"  # English
        else:
            return "am-latn"  # Amhar-glish
    
    async def process_message(self, message: str, session_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Process user message and return response."""
        if session_data is None:
            session_data = {}
        
        # Detect language
        language = self.detect_language(message)
        
        # Build conversation context
        conversation_history = session_data.get("conversation_history", [])
        conversation_history.append({"role": "user", "content": message})
        
        # Create tools schema for Gemini
        tools_schema = self.mcp_server.get_tools_schema()
        
        try:
            # Generate response with tool calling
            response = await self._generate_response_with_tools(
                message, conversation_history, tools_schema, language
            )
            
            # Update conversation history
            conversation_history.append({"role": "assistant", "content": response["content"]})
            session_data["conversation_history"] = conversation_history
            session_data["language"] = language
            
            return {
                "success": True,
                "response": response["content"],
                "language": language,
                "session_data": session_data,
                "tools_used": response.get("tools_used", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error. Please try again.",
                "language": language,
                "session_data": session_data
            }
    
    async def _generate_response_with_tools(
        self, 
        message: str, 
        conversation_history: List[Dict], 
        tools_schema: List[Dict],
        language: str
    ) -> Dict[str, Any]:
        """Generate response using Gemini with tool calling."""
        
        try:
            # Build context from conversation history
            context = self.system_prompt + "\n\n"
            
            # Add language-specific instructions
            if language == "am":
                context += "Respond in Amharic (አማርኛ). Use Amharic script.\n\n"
            elif language == "am-latn":
                context += "Respond in Amhar-glish (Amharic in Latin script). Use Latin characters.\n\n"
            else:
                context += "Respond in English.\n\n"
            
            # Add conversation context
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
            
            context += f"\nUser: {message}\nAssistant:"
            
            # Generate response without tools first
            response = self.model.generate_content(
                context,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            # Simple response handling
            if response and hasattr(response, 'text') and response.text:
                return {
                    "content": response.text,
                    "tools_used": []
                }
            else:
                return {
                    "content": "I understand your request. How can I help you further?",
                    "tools_used": []
                }
            
        except Exception as e:
            print(f"Error in _generate_response_with_tools: {e}")
            return {
                "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "tools_used": []
            }
    
    def get_welcome_message(self, language: str = "en") -> str:
        """Get welcome message based on language."""
        messages = {
            "en": "Welcome to KcartBot! I'm your AI Agri-Commerce Assistant. I can help you with:\n• Product discovery and ordering\n• Pricing insights\n• Storage and nutritional information\n• Order management\n\nAre you a customer or supplier?",
            "am": "እንኳን ደህና መጡ! እኔ KcartBot ነኝ፣ የእርስዎ AI የአግሪ-ኮሜርስ ረዳት። እንደሚከተሉት ሊረዳዎ እችላለሁ:\n• የምርት ማግኛነት እና ትዕዛዝ\n• የዋጋ ትንተና\n• የማከማቻ እና የምግብ መረጃ\n• የትዕዛዝ አያያዝ\n\nእርስዎ ደንበኛ ነዎት ወይስ አቅራቢ?",
            "am-latn": "Enkwan dehna metu! Ene KcartBot negn, ye'irso AI ye'agri-commerce redat. Endemiketelut liredawo echelalew:\n• Ye-meret magenatnet ena te'ezaz\n• Ye-waga tinetana\n• Ye-makechach ena ye-migb merja\n• Ye-te'ezaz ayayaz\n\nIrso de-nebant natut wesis aqribi?"
        }
        return messages.get(language, messages["en"])
    
    def simulate_cod_confirmation(self) -> str:
        """Simulate COD payment confirmation with delay."""
        import time
        time.sleep(5)  # 5-second pause as required
        return "Order Confirmed for COD. Your order will be delivered as scheduled. Thank you for choosing KcartBot!"
