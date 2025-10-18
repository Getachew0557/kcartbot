import streamlit as st
import asyncio

def render_chat_tab(chat_service):
    """Render the chat interface tab."""
    st.markdown('<h2 class="sub-header">💬 Chat with KcartBot</h2>', unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.session_data = {}
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>KcartBot:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your message here...", key="chat_input", value="", help="Enter your message and press Enter or click Send")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Send Message", type="primary"):
            if user_input and user_input.strip():
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Regular chat processing
                try:
                    result = asyncio.run(chat_service.process_message(
                        user_input, 
                        st.session_state.session_data
                    ))
                    
                    if result["success"]:
                        # Add bot response
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": result["response"]
                        })
                        st.session_state.session_data = result["session_data"]
                        
                        # Show tools used if any
                        if result.get("tools_used"):
                            st.info(f"🔧 Tools used: {', '.join([tool['tool'] for tool in result['tools_used']])}")
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"Error processing message: {e}")
                
                # Clear input and rerun
                st.rerun()
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_data = {}
            st.rerun()
    
    with col3:
        if st.button("Get Welcome Message"):
            language = st.session_state.get("language_select", "English")
            lang_map = {"English": "en", "Amharic (አማርኛ)": "am", "Amhar-glish": "am-latn"}
            welcome_msg = chat_service.get_welcome_message(lang_map[language])
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()