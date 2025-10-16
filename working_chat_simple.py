"""Simple Working Chat Interface for KcartBot - No Gemini Dependency"""

import streamlit as st
import sqlite3
import sys
import os

def get_simple_response(message):
    """Get a simple response based on keywords."""
    
    message_lower = message.lower()
    
    # Customer registration
    if "register" in message_lower and "customer" in message_lower:
        return "Welcome! Please provide your name and phone number to complete registration as a customer."
    
    # Supplier registration  
    elif "register" in message_lower and "supplier" in message_lower:
        return "Welcome! Please provide your name and phone number to complete registration as a supplier."
    
    # Order requests
    elif "order" in message_lower and any(word in message_lower for word in ["tomato", "onion", "potato", "milk", "avocado"]):
        if "tomato" in message_lower:
            return "I found tomatoes available at 40.43 ETB/kg. How many kg would you like to order?"
        elif "onion" in message_lower:
            return "I found red onions available at 46.81 ETB/kg. How many kg would you like to order?"
        elif "potato" in message_lower:
            return "I found potatoes available at 30.64 ETB/kg. How many kg would you like to order?"
        elif "milk" in message_lower:
            return "I found fresh milk available at 45.00 ETB/liter. How many liters would you like to order?"
        elif "avocado" in message_lower:
            return "I found avocados available at 35.64 ETB/kg. How many kg would you like to order?"
    
    # Storage questions
    elif "store" in message_lower or "storage" in message_lower:
        if "tomato" in message_lower:
            return "Store tomatoes at room temperature until ripe, then refrigerate for longer shelf life. They're rich in lycopene and vitamin C."
        elif "avocado" in message_lower:
            return "Store unripe avocados at room temperature, refrigerate when ripe. They're high in healthy monounsaturated fats and fiber."
        elif "milk" in message_lower:
            return "Store fresh milk in the refrigerator at 4°C or below. It should be consumed within 3-5 days of purchase."
        else:
            return "I can help you with storage tips for various products. Which product would you like storage advice for?"
    
    # Pricing questions
    elif "price" in message_lower:
        if "tomato" in message_lower:
            return "Tomatoes are currently priced at 40.43 ETB per kg."
        elif "onion" in message_lower:
            return "Red onions are currently priced at 46.81 ETB per kg."
        elif "potato" in message_lower:
            return "Potatoes are currently priced at 30.64 ETB per kg."
        elif "milk" in message_lower:
            return "Fresh milk is currently priced at 45.00 ETB per liter."
        else:
            return "I can help you with pricing information. Which product would you like to know the price for?"
    
    # Supplier functions
    elif "add" in message_lower and "product" in message_lower:
        return "I can help you add products. Please tell me the product name, category (horticulture or dairy), quantity, and price."
    
    elif "check" in message_lower and "order" in message_lower:
        return "I can help you check your orders. As a supplier, you can view pending orders and manage your inventory."
    
    # General help
    elif "help" in message_lower or "what can you do" in message_lower:
        return """I'm KcartBot, your AI Agri-Commerce Assistant! I can help you with:

**For Customers:**
• Register as a customer
• Order products (tomatoes, onions, potatoes, milk, etc.)
• Get storage tips
• Check prices
• Learn about products

**For Suppliers:**
• Register as a supplier  
• Add products to inventory
• Check orders
• Get pricing insights
• Manage stock

Just tell me what you'd like to do!"""
    
    # Greeting
    elif any(word in message_lower for word in ["hello", "hi", "salam", "ሰላም"]):
        return "Hello! Welcome to KcartBot! I'm your AI Agri-Commerce Assistant. How can I help you today?"
    
    # Default response
    else:
        return f"I understand you said: '{message}'. How can I help you today? You can ask me about:\n\n• Registering as a customer or supplier\n• Ordering products\n• Getting storage tips\n• Checking prices\n• Managing inventory"

def main():
    """Main chat interface."""
    st.title("🌱 KcartBot Chat Interface")
    st.markdown("Chat with your AI Agri-Commerce Assistant!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_simple_response(prompt)
                st.markdown(response)
        
        # Add bot response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with example messages
    with st.sidebar:
        st.markdown("### 💡 Try these examples:")
        
        example_messages = [
            "I want to register as a customer",
            "I'm a supplier, I want to register",
            "I want to order some tomatoes",
            "How should I store avocados?",
            "What's the price of red onions?",
            "Check my orders",
            "I want to add potatoes",
            "Help me"
        ]
        
        for example in example_messages:
            if st.button(example, key=f"example_{example}"):
                # Add example to chat
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Database stats
        st.markdown("### 📊 Quick Stats")
        try:
            conn = sqlite3.connect('kcartbot.db')
            
            users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            products_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            
            st.metric("Users", f"{users_count:,}")
            st.metric("Products", f"{products_count:,}")
            st.metric("Orders", f"{orders_count:,}")
            
            conn.close()
        except Exception as e:
            st.error(f"Error loading stats: {e}")

if __name__ == "__main__":
    main()
