from .database import get_db_connection, execute_query
from .chat import render_chat_tab
from .analytics import render_analytics_tab
from .products import render_products_tab
from .orders import render_orders_tab
from .knowledge import render_knowledge_tab
from .styles import get_custom_css

from src.services.chat_service import GeminiChatService
from src.services.rag_service import RAGService
from src.mcp.server import MCPServer
import streamlit as st

@st.cache_resource
def init_services():
    """Initialize KcartBot services."""
    try:
        chat_service = GeminiChatService()
        rag_service = RAGService()
        mcp_server = MCPServer()
        return chat_service, rag_service, mcp_server
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None

def setup_page_config():
    """Set up Streamlit page configuration."""
    st.set_page_config(
        page_title="KcartBot Dashboard",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar():
    """Render the sidebar with quick actions and stats."""
    with st.sidebar:
        # Clean logo section
        st.markdown("""
        <div style="padding: 1.5rem 0;">
            <div style="font-size: 3rem; margin-left: 2.5rem;">🌱</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        st.markdown("### 🎯 Quick Actions")
        
        # Language selection
        language = st.selectbox(
            "🌍 Language",
            ["English", "Amharic (አማርኛ)", "Amhar-glish"],
            index=0,
            key="language_select"
        )
        
        # User type selection
        user_type = st.selectbox(
            "👤 User Type",
            ["Customer", "Supplier"],
            index=0,
            key="user_type_select"
        )
        
        st.markdown("---")
        
        # Database stats
        st.markdown("### 📊 Database Stats")
        
        try:
            users_count = execute_query("SELECT COUNT(*) as count FROM users").iloc[0]['count']
            products_count = execute_query("SELECT COUNT(*) as count FROM products").iloc[0]['count']
            orders_count = execute_query("SELECT COUNT(*) as count FROM orders").iloc[0]['count']
            knowledge_count = execute_query("SELECT COUNT(*) as count FROM product_knowledge").iloc[0]['count']
            
            st.metric("Users", f"{users_count:,}")
            st.metric("Products", f"{products_count:,}")
            st.metric("Orders", f"{orders_count:,}")
            st.metric("Knowledge", f"{knowledge_count:,}")
        except Exception as e:
            st.error(f"Error loading stats: {e}")

def render_main_content(chat_service, rag_service, mcp_server):
    """Render the main content with tabs."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat Interface", "📊 Analytics", "🛒 Products", "📦 Orders", "🧠 Knowledge Base"])
    
    with tab1:
        render_chat_tab(chat_service)
    
    with tab2:
        render_analytics_tab()
    
    with tab3:
        render_products_tab()
    
    with tab4:
        render_orders_tab()
    
    with tab5:
        render_knowledge_tab(rag_service, chat_service)