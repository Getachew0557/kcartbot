from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import time
from src.llm.gemini_client import GeminiClient
from src.mcp.tools import MCPTools
from src.rag.vector_store import VectorStore
from src.database.models import User, Supplier, Product, Order
from src.chat.lang import detect_language, normalize_amhar_glish
import uuid

class CustomerFlow:
    def __init__(self, db: Session, user_id=None):
        self.db = db
        self.user_id = user_id
        self.llm = GeminiClient()
        self.mcp_tools = MCPTools(db)
        self.vector_store = VectorStore()
        self.current_order = {}
    
    def handle_message(self, message):
        """Handle customer messages with appropriate flow"""
        language = detect_language(message)
        normalized_message = normalize_amhar_glish(message) if language == "amhar-glish" else message
        
        # Check if user is registered
        if not self.user_id:
            return self.handle_registration(normalized_message, language)
        
        # Check for knowledge questions
        if self.is_knowledge_question(normalized_message):
            return self.handle_knowledge_question(normalized_message, language)
        
        # Check for ordering intent
        if self.is_ordering_intent(normalized_message):
            return self.handle_ordering(normalized_message, language)
        
        # Default response
        return self.generate_default_response(normalized_message, language)
    
    def handle_registration(self, message, language):
        """Handle customer registration"""
        # Simple registration - extract name and phone
        if language == "amharic":
            response = "እንኳን ወደ KcartBot በደህና መጡ! ስሞን እና ስልክ ቁጥርዎን ያስገቡ።"
        elif language == "amhar-glish":
            response = "Welcome to KcartBot! Please provide your name and phone number."
        else:
            response = "Welcome to KcartBot! Please provide your name and phone number."
        
        # Simple name and phone extraction (in real implementation, use proper NLP)
        if "my name is" in message.lower() or "I am" in message.lower():
            # Extract name and phone (simplified)
            name = "Customer"  # In real implementation, extract properly
            phone = "0000000000"
            
            # Create user
            user = User(
                name=name,
                phone=phone,
                location="Addis Ababa",  # Default
                user_type="customer"
            )
            self.db.add(user)
            self.db.commit()
            self.user_id = user.id
            
            if language == "amharic":
                response = f"እንኳን ደህና መጡ {name}! አሁን ምርቶችን መጠየቅ ወይም መረጃ መጠየቅ ትችላለህ።"
            else:
                response = f"Welcome {name}! You can now ask about products or place orders."
        
        return response
    
    def is_knowledge_question(self, message):
        """Check if message is a knowledge question"""
        knowledge_keywords = ['how to', 'what is', 'how do i', 'storage', 'store', 'calorie', 'recipe', 'nutrition']
        return any(keyword in message.lower() for keyword in knowledge_keywords)
    
    def handle_knowledge_question(self, message, language):
        """Handle knowledge questions using RAG"""
        # Query vector store
        language_filter = language if language in ["english", "amharic"] else None
        results = self.vector_store.query(message, language_filter=language_filter)
        
        if results['documents']:
            # Use the most relevant result
            answer = results['documents'][0][0]
            return answer.split("A: ")[1] if "A: " in answer else answer
        else:
            # Fallback to LLM
            return self.llm.generate_response(f"Answer this question about agricultural products: {message}")
    
    def is_ordering_intent(self, message):
        """Check if message contains ordering intent"""
        order_keywords = ['i want', 'order', 'buy', 'need', 'kg', 'liter', 'kilo']
        return any(keyword in message.lower() for keyword in order_keywords)
    
    def handle_ordering(self, message, language):
        """Handle product ordering"""
        # Simplified order parsing (in real implementation, use proper NLP)
        if "onion" in message.lower():
            product_name = "Red Onion"
            quantity = 1  # Default
        elif "tomato" in message.lower():
            product_name = "Tomato"
            quantity = 1
        elif "milk" in message.lower():
            product_name = "Milk"
            quantity = 1
        else:
            # Use LLM to extract product and quantity
            extraction_prompt = f"""
            Extract product name and quantity from this order message: "{message}"
            Return format: PRODUCT_NAME|QUANTITY
            Default quantity is 1 if not specified.
            """
            extraction = self.llm.generate_response(extraction_prompt)
            try:
                product_name, quantity_str = extraction.split("|")
                quantity = float(quantity_str)
            except:
                product_name = "Unknown"
                quantity = 1
        
        # Check product availability
        product = self.db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
        if not product:
            return f"Sorry, {product_name} is not available."
        
        if product.stock_quantity < quantity:
            return f"Sorry, only {product.stock_quantity} {product.unit} of {product_name} available."
        
        # Store order details
        self.current_order = {
            'product_id': product.id,
            'product_name': product_name,
            'quantity': quantity,
            'price': product.current_price,
            'total': quantity * product.current_price
        }
        
        response = f"Great! {quantity} {product.unit} of {product_name} at {product.current_price} ETB per {product.unit}. Total: {quantity * product.current_price} ETB.\n"
        response += "Please provide delivery date and location."
        
        return response
    
    def complete_order(self, delivery_date, delivery_location):
        """Complete the order with COD simulation"""
        if not self.current_order:
            return "No active order to complete."
        
        # Create order
        order = Order(
            user_id=self.user_id,
            product_id=self.current_order['product_id'],
            quantity=self.current_order['quantity'],
            delivery_date=delivery_date,
            delivery_location=delivery_location,
            status="confirmed"
        )
        self.db.add(order)
        self.db.commit()
        
        # Simulate COD confirmation
        response = f"Order confirmed! {self.current_order['quantity']} {self.current_order['product_name']} will be delivered to {delivery_location} on {delivery_date}.\n"
        response += "Payment is Cash on Delivery. Confirming order..."
        
        # Simulate 5-second pause
        time.sleep(5)
        
        response += "\nOrder Confirmed for COD."
        
        # Clear current order
        self.current_order = {}
        
        return response
    
    def generate_default_response(self, message, language):
        """Generate default response using LLM"""
        context = "You are KcartBot, an agricultural commerce assistant in Ethiopia. Help customers with product inquiries and orders."
        return self.llm.generate_response(message, context)

class SupplierFlow:
    def __init__(self, db: Session, supplier_id=None):
        self.db = db
        self.supplier_id = supplier_id
        self.llm = GeminiClient()
        self.mcp_tools = MCPTools(db)
    
    def handle_message(self, message):
        """Handle supplier messages"""
        language = detect_language(message)
        
        if not self.supplier_id:
            return self.handle_registration(message, language)
        
        if "add" in message.lower() and any(product in message.lower() for product in ["tomato", "onion", "milk", "avocado"]):
            return self.handle_product_addition(message, language)
        
        if "check my stock" in message.lower():
            return self.mcp_tools.check_supplier_stock(self.get_supplier_name())
        
        if "deliveries" in message.lower() or "schedule" in message.lower():
            return self.handle_schedule_query(message, language)
        
        if "expire" in message.lower() or "flash sale" in message.lower():
            return self.mcp_tools.get_expiry_nudge(self.get_supplier_name())
        
        return self.generate_default_response(message, language)
    
    def handle_registration(self, message, language):
        """Handle supplier registration"""
        # Extract supplier name
        supplier_name = "Supplier"  # In real implementation, extract properly
        
        supplier = Supplier(
            name=supplier_name,
            phone="0000000000"  # Default
        )
        self.db.add(supplier)
        self.db.commit()
        self.supplier_id = supplier.id
        
        return f"Welcome supplier {supplier_name}! You can now add products and check your stock."
    
    def get_supplier_name(self):
        """Get supplier name from ID"""
        supplier = self.db.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        return supplier.name if supplier else "Unknown"
    
    def handle_product_addition(self, message, language):
        """Handle adding new products"""
        # Extract product name from message
        product_name = "Tomato"  # Default, in real implementation use NLP
        
        # Get pricing insights
        pricing_insight = self.mcp_tools.get_competitor_pricing(product_name)
        
        response = f"Okay, for {product_name}. {pricing_insight}\n"
        response += "What quantity (kg) and available delivery dates for this batch?"
        
        return response
    
    def handle_schedule_query(self, message, language):
        """Handle schedule queries"""
        # Extract date if mentioned
        date = None
        if "tuesday" in message.lower():
            # Find next Tuesday
            today = datetime.now()
            days_ahead = (1 - today.weekday() + 7) % 7  # 1 is Tuesday
            if days_ahead == 0:  # Today is Tuesday
                days_ahead = 7
            next_tuesday = today + timedelta(days=days_ahead)
            date = next_tuesday.strftime("%Y-%m-%d")
        
        return self.mcp_tools.get_supplier_schedule(self.get_supplier_name(), date)
    
    def generate_default_response(self, message, language):
        """Generate default response for suppliers"""
        context = "You are KcartBot assistant for suppliers. Help with product management, pricing insights, and delivery scheduling."
        return self.llm.generate_response(message, context)