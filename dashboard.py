"""KcartBot Interactive Web Dashboard"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our services
try:
    from src.services.chat_service import GeminiChatService
    from src.services.rag_service import RAGService
    from src.mcp.server import MCPServer
except ImportError:
    st.error("Could not import KcartBot services. Please ensure all dependencies are installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="KcartBot Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #228B22;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
    }
    .chat-message {
        padding: 15px;
        margin: 10px 0;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-weight: 500;
        color: white;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-left: 20%;
        text-align: right;
    }
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        margin-right: 20%;
        text-align: left;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .chat-input {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .chat-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
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

# Database connection
def get_db_connection():
    """Get database connection."""
    return sqlite3.connect('kcartbot.db', check_same_thread=False)

def execute_query(query, params=None):
    """Execute a database query and return results."""
    conn = get_db_connection()
    try:
        if params:
            result = pd.read_sql_query(query, conn, params=params)
        else:
            result = pd.read_sql_query(query, conn)
        return result
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Initialize services
chat_service, rag_service, mcp_server = init_services()

if chat_service is None:
    st.error("Failed to initialize KcartBot services. Please check your configuration.")
    st.stop()

# Main header
st.markdown('<h1 class="main-header">🌱 KcartBot Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced AI Agri-Commerce Assistant for Ethiopia</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/2E8B57/FFFFFF?text=KcartBot", width=200)
    
    st.markdown("### 🎯 Quick Actions")
    
    # Language selection
    language = st.selectbox(
        "🌍 Language",
        ["English", "Amharic (አማርኛ)", "Amhar-glish"],
        index=0
    )
    
    # User type selection
    user_type = st.selectbox(
        "👤 User Type",
        ["Customer", "Supplier"],
        index=0
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

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat Interface", "📊 Analytics", "🛒 Products", "📦 Orders", "🧠 Knowledge Base"])

# Chat Interface Tab
with tab1:
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
                
                # Get bot response
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
            lang_map = {"English": "en", "Amharic (አማርኛ)": "am", "Amhar-glish": "am-latn"}
            welcome_msg = chat_service.get_welcome_message(lang_map[language])
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()

# Analytics Tab
with tab2:
    st.markdown('<h2 class="sub-header">📊 Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    try:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = execute_query("SELECT COUNT(*) as count FROM users").iloc[0]['count']
            st.metric("Total Users", f"{total_users:,}")
        
        with col2:
            total_products = execute_query("SELECT COUNT(*) as count FROM products").iloc[0]['count']
            st.metric("Total Products", f"{total_products:,}")
        
        with col3:
            total_orders = execute_query("SELECT COUNT(*) as count FROM orders").iloc[0]['count']
            st.metric("Total Orders", f"{total_orders:,}")
        
        with col4:
            total_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders").iloc[0]['total']
            st.metric("Total Revenue", f"ETB {total_revenue:,.2f}")
    except Exception as e:
        st.error(f"Error loading metrics: {e}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            # User type distribution
            user_types = execute_query("""
                SELECT user_type, COUNT(*) as count 
                FROM users 
                GROUP BY user_type
            """)
            
            if not user_types.empty:
                fig_users = px.pie(user_types, values='count', names='user_type', 
                                  title="User Type Distribution",
                                  color_discrete_map={'customer': '#2E8B57', 'supplier': '#228B22'})
                st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Product category distribution
            product_cats = execute_query("""
                SELECT category, COUNT(*) as count 
                FROM products 
                GROUP BY category
            """)
            
            if not product_cats.empty:
                fig_products = px.bar(product_cats, x='category', y='count',
                                    title="Products by Category",
                                    color='category',
                                    color_discrete_map={'horticulture': '#2E8B57', 'dairy': '#228B22'})
                st.plotly_chart(fig_products, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading charts: {e}")
    
    # Order trends
    st.markdown("### 📈 Order Trends")
    
    try:
        # Get orders by date
        orders_by_date = execute_query("""
            SELECT DATE(created_at) as date, COUNT(*) as orders, SUM(total_amount) as revenue
            FROM orders 
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        if not orders_by_date.empty:
            fig_trends = px.line(orders_by_date, x='date', y='orders',
                               title="Orders Over Last 30 Days",
                               color_discrete_sequence=['#2E8B57'])
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("No order data available for the last 30 days.")
    except Exception as e:
        st.error(f"Error loading order trends: {e}")

# Products Tab
with tab3:
    st.markdown('<h2 class="sub-header">🛒 Product Management</h2>', unsafe_allow_html=True)
    
    # Product search
    search_query = st.text_input("🔍 Search Products", placeholder="Enter product name...")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        category_filter = st.selectbox("Category", ["All", "horticulture", "dairy"])
    
    with col2:
        sort_by = st.selectbox("Sort by", ["name", "current_price", "quantity_available"])
    
    try:
        # Get products
        query = """
            SELECT p.name, p.name_amharic, p.category, p.unit, p.current_price, 
                   p.quantity_available, p.expiry_date, u.name as supplier_name
            FROM products p
            JOIN users u ON p.supplier_id = u.id
            WHERE p.is_active = 1
        """
        
        if search_query:
            query += f" AND (p.name LIKE '%{search_query}%' OR p.name_amharic LIKE '%{search_query}%')"
        
        if category_filter != "All":
            query += f" AND p.category = '{category_filter}'"
        
        query += f" ORDER BY p.{sort_by}"
        
        products_df = execute_query(query)
    except Exception as e:
        st.error(f"Error loading products: {e}")
        products_df = pd.DataFrame()
    
    if not products_df.empty:
        # Display products in a nice format
        for idx, row in products_df.iterrows():
            with st.expander(f"{row['name']} - ETB {row['current_price']:.2f}/{row['unit']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Supplier:** {row['supplier_name']}")
                
                with col2:
                    st.write(f"**Available:** {row['quantity_available']:.1f} {row['unit']}")
                    st.write(f"**Price:** ETB {row['current_price']:.2f}")
                
                with col3:
                    if row['expiry_date']:
                        expiry = datetime.fromisoformat(row['expiry_date'])
                        days_left = (expiry - datetime.now()).days
                        if days_left < 0:
                            st.error(f"Expired {abs(days_left)} days ago")
                        elif days_left <= 3:
                            st.warning(f"Expires in {days_left} days")
                        else:
                            st.success(f"Expires in {days_left} days")
                    else:
                        st.info("No expiry date")
    else:
        st.info("No products found matching your criteria.")

# Orders Tab
with tab4:
    st.markdown('<h2 class="sub-header">📦 Order Management</h2>', unsafe_allow_html=True)
    
    # Order filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "pending", "confirmed", "delivered", "cancelled"])
    
    with col2:
        days_filter = st.selectbox("Time Range", ["All", "Today", "Last 7 days", "Last 30 days"])
    
    with col3:
        user_type_filter = st.selectbox("User Type", ["All", "customer", "supplier"])
    
    try:
        # Build query
        query = """
            SELECT o.id, o.created_at, o.status, o.total_amount, o.quantity_ordered,
                   u.name as customer_name, p.name as product_name, p.unit
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            WHERE 1=1
        """
        
        if status_filter != "All":
            query += f" AND o.status = '{status_filter}'"
        
        if days_filter != "All":
            if days_filter == "Today":
                query += " AND DATE(o.created_at) = DATE('now')"
            elif days_filter == "Last 7 days":
                query += " AND o.created_at >= date('now', '-7 days')"
            elif days_filter == "Last 30 days":
                query += " AND o.created_at >= date('now', '-30 days')"
        
        if user_type_filter != "All":
            query += f" AND u.user_type = '{user_type_filter}'"
        
        query += " ORDER BY o.created_at DESC LIMIT 50"
        
        orders_df = execute_query(query)
    except Exception as e:
        st.error(f"Error loading orders: {e}")
        orders_df = pd.DataFrame()
    
    if not orders_df.empty:
        # Display orders
        for idx, row in orders_df.iterrows():
            status_color = {
                "pending": "🟡",
                "confirmed": "🟢", 
                "delivered": "✅",
                "cancelled": "❌"
            }
            
            with st.expander(f"{status_color.get(row['status'], '❓')} Order #{row['id'][:8]} - {row['customer_name']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Product:** {row['product_name']}")
                    st.write(f"**Quantity:** {row['quantity_ordered']} {row['unit']}")
                
                with col2:
                    st.write(f"**Total:** ETB {row['total_amount']:.2f}")
                    st.write(f"**Status:** {row['status'].title()}")
                
                with col3:
                    st.write(f"**Date:** {row['created_at']}")
    else:
        st.info("No orders found matching your criteria.")

# Knowledge Base Tab
with tab5:
    st.markdown('<h2 class="sub-header">🧠 Product Knowledge Base</h2>', unsafe_allow_html=True)
    
    # Knowledge search
    knowledge_query = st.text_input("🔍 Search Knowledge", placeholder="e.g., storage tips, nutritional info...")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        knowledge_type = st.selectbox("Knowledge Type", ["All", "storage", "nutrition", "recipe", "seasonal"])
    
    with col2:
        if st.button("Search Knowledge"):
            if knowledge_query:
                try:
                    results = rag_service.search_knowledge(
                        query=knowledge_query,
                        knowledge_type=knowledge_type if knowledge_type != "All" else None,
                        limit=10
                    )
                    
                    if results:
                        st.success(f"Found {len(results)} knowledge items")
                        
                        for result in results:
                            with st.expander(f"{result['metadata']['knowledge_type'].title()}: {result['content'][:50]}..."):
                                st.write(f"**Content:** {result['content']}")
                                st.write(f"**Type:** {result['metadata']['knowledge_type']}")
                                st.write(f"**Language:** {result['metadata']['language']}")
                    else:
                        st.info("No knowledge found for your query.")
                        
                except Exception as e:
                    st.error(f"Error searching knowledge: {e}")
    
    # Knowledge statistics
    st.markdown("### 📊 Knowledge Statistics")
    
    try:
        stats = rag_service.get_knowledge_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Items", f"{stats['total_items']:,}")
        
        with col2:
            st.metric("Knowledge Types", len(stats['knowledge_types']))
        
        with col3:
            st.metric("Languages", len(stats['languages']))
        
        # Knowledge type distribution
        if stats['knowledge_types']:
            knowledge_df = pd.DataFrame(list(stats['knowledge_types'].items()), 
                                      columns=['Type', 'Count'])
            fig_knowledge = px.pie(knowledge_df, values='Count', names='Type',
                                 title="Knowledge Distribution by Type")
            st.plotly_chart(fig_knowledge, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error getting knowledge stats: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 <strong>KcartBot</strong> - Empowering Ethiopian agriculture through AI-driven commerce!</p>
    <p>Built with ❤️ using Streamlit, Gemini AI, and modern web technologies</p>
</div>
""", unsafe_allow_html=True)
