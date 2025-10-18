import streamlit as st
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import dashboard components
from src.dashboard import (
    init_services,
    setup_page_config,
    render_sidebar,
    render_main_content,
    get_custom_css
)

# Page configuration
setup_page_config()

# Custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize services
chat_service, rag_service, mcp_server = init_services()

if chat_service is None:
    st.error("Failed to initialize KcartBot services. Please check your configuration.")
    st.stop()

# Main header
st.markdown('<h1 class="main-header">🌱 KcartBot Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced AI Agri-Commerce Assistant for Ethiopia</p>', unsafe_allow_html=True)

# Sidebar
render_sidebar()

# Main content tabs
render_main_content(chat_service, rag_service, mcp_server)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 <strong>KcartBot</strong> - Empowering Ethiopian agriculture through AI-driven commerce!</p>
    <p>Built with ❤️ using Streamlit, Gemini AI, and modern web technologies</p>
</div>
""", unsafe_allow_html=True)