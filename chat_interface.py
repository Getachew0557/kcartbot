"""Simplified Chat Interface for KcartBot Dashboard"""

import streamlit as st
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def get_chat_response(message):
    """Get chat response using a simplified approach."""
    try:
        from src.services.chat_service import GeminiChatService
        
        # Initialize chat service
        chat_service = GeminiChatService()
        
        # Process message
        result = asyncio.run(chat_service.process_message(message))
        
        if result["success"]:
            return result["response"]
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Error: {str(e)}"

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
                response = get_chat_response(prompt)
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
            "I want to add potatoes"
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

if __name__ == "__main__":
    main()
