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
    st.markdown('<h2 class="sub-header">📊 Dynamic Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Analytics", type="secondary"):
        st.rerun()
    
    try:
        # Enhanced Key metrics with trends
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = execute_query("SELECT COUNT(*) as count FROM users").iloc[0]['count']
            active_users = execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1").iloc[0]['count']
            new_users_week = execute_query("SELECT COUNT(*) as count FROM users WHERE created_at >= date('now', '-7 days')").iloc[0]['count']
            st.metric("Total Users", f"{total_users:,}", f"+{new_users_week} this week")
            st.caption(f"{active_users} active users")
        
        with col2:
            total_products = execute_query("SELECT COUNT(*) as count FROM products").iloc[0]['count']
            available_products = execute_query("SELECT COUNT(*) as count FROM products WHERE quantity_available > 0").iloc[0]['count']
            avg_price = execute_query("SELECT AVG(current_price) as avg_price FROM products WHERE current_price > 0").iloc[0]['avg_price'] or 0
            st.metric("Total Products", f"{total_products:,}", f"{available_products} available")
            st.caption(f"Avg price: ETB {avg_price:.2f}")
        
        with col3:
            total_orders = execute_query("SELECT COUNT(*) as count FROM orders").iloc[0]['count']
            recent_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE created_at >= date('now', '-7 days')").iloc[0]['count']
            pending_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'").iloc[0]['count']
            st.metric("Total Orders", f"{total_orders:,}", f"+{recent_orders} this week")
            st.caption(f"{pending_orders} pending orders")
        
        with col4:
            total_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders").iloc[0]['total'] or 0
            weekly_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders WHERE created_at >= date('now', '-7 days')").iloc[0]['total'] or 0
            avg_order_value = execute_query("SELECT AVG(total_amount) as avg_value FROM orders WHERE total_amount > 0").iloc[0]['avg_value'] or 0
            st.metric("Total Revenue", f"ETB {total_revenue:,.2f}", f"ETB {weekly_revenue:,.2f} this week")
            st.caption(f"Avg order: ETB {avg_order_value:.2f}")
    except Exception as e:
        st.error(f"Error loading metrics: {e}")
    
    # Enhanced Charts Section
    st.markdown("### 📈 Advanced Analytics")
    
    # Row 1: User and Product Analytics
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            # User analytics with more details
            user_types = execute_query("""
                SELECT user_type, COUNT(*) as count 
                FROM users 
                GROUP BY user_type
            """)
            
            if not user_types.empty:
                fig_users = px.pie(user_types, values='count', names='user_type', 
                                  title="User Type Distribution",
                                  color_discrete_map={'customer': '#2E8B57', 'supplier': '#228B22'})
                fig_users.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Product analytics with pricing
            product_cats = execute_query("""
                SELECT category, COUNT(*) as count, AVG(current_price) as avg_price
                FROM products 
                GROUP BY category
            """)
            
            if not product_cats.empty:
                fig_products = px.bar(product_cats, x='category', y='avg_price',
                                    title="Average Price by Category",
                                    color='category',
                                    color_discrete_sequence=['#2E8B57', '#228B22', '#32CD32'])
                fig_products.update_layout(yaxis_title="Average Price (ETB)")
                st.plotly_chart(fig_products, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading charts: {e}")
    
    # Row 2: Order and Revenue Analytics
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            # Order trends with dual y-axis
            orders_by_date = execute_query("""
                SELECT DATE(created_at) as date, COUNT(*) as order_count, SUM(total_amount) as total_revenue
                FROM orders 
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            
            if not orders_by_date.empty:
                fig_orders = go.Figure()
                fig_orders.add_trace(go.Scatter(
                    x=orders_by_date['date'],
                    y=orders_by_date['order_count'],
                    mode='lines+markers',
                    name='Orders',
                    line=dict(color='#2E8B57', width=3)
                ))
                fig_orders.update_layout(
                    title="Orders Over Last 30 Days",
                    xaxis_title="Date",
                    yaxis_title="Number of Orders",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_orders, use_container_width=True)
        
        with col2:
            # Revenue trends
            if not orders_by_date.empty:
                fig_revenue = go.Figure()
                fig_revenue.add_trace(go.Scatter(
                    x=orders_by_date['date'],
                    y=orders_by_date['total_revenue'],
                    mode='lines+markers',
                    name='Revenue',
                    line=dict(color='#228B22', width=3),
                    fill='tonexty'
                ))
                fig_revenue.update_layout(
                    title="Revenue Over Last 30 Days",
                    xaxis_title="Date",
                    yaxis_title="Revenue (ETB)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_revenue, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading trend charts: {e}")
    
    # Row 3: Pricing and Supplier Analytics
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            # Pricing trends
            pricing_data = execute_query("""
                SELECT p.name as product_name, p.current_price, p.category
                FROM products p
                WHERE p.current_price > 0
                ORDER BY p.current_price DESC
                LIMIT 15
            """)
            
            if not pricing_data.empty:
                fig_pricing = px.bar(pricing_data, x='product_name', y='current_price',
                                    title="Top 15 Products by Price",
                                    color='category',
                                    color_discrete_map={'horticulture': '#2E8B57', 'dairy': '#228B22'})
                fig_pricing.update_layout(xaxis_tickangle=-45, yaxis_title="Price (ETB)")
                st.plotly_chart(fig_pricing, use_container_width=True)
        
        with col2:
            # Supplier performance
            supplier_performance = execute_query("""
                SELECT u.name as supplier_name, 
                       COUNT(DISTINCT p.id) as product_count,
                       COUNT(o.id) as order_count,
                       SUM(o.total_amount) as total_revenue,
                       AVG(o.total_amount) as avg_order_value
                FROM users u
                LEFT JOIN products p ON u.id = p.supplier_id
                LEFT JOIN orders o ON p.id = o.product_id
                WHERE u.user_type = 'supplier'
                GROUP BY u.id, u.name
                HAVING order_count > 0
                ORDER BY total_revenue DESC
                LIMIT 10
            """)
            
            if not supplier_performance.empty:
                fig_suppliers = px.scatter(supplier_performance, 
                                         x='product_count', y='total_revenue',
                                         size='order_count',
                                         hover_name='supplier_name',
                                         title="Supplier Performance",
                                         color='avg_order_value',
                                         color_continuous_scale='Greens')
                fig_suppliers.update_layout(
                    xaxis_title="Number of Products",
                    yaxis_title="Total Revenue (ETB)"
                )
                st.plotly_chart(fig_suppliers, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading performance charts: {e}")
    
    # Detailed analytics tables
    st.markdown("### 📋 Detailed Analytics")
    
    tab_analytics1, tab_analytics2, tab_analytics3, tab_analytics4 = st.tabs(["👥 Users", "🛒 Products", "📦 Orders", "💰 Revenue"])
    
    with tab_analytics1:
        try:
            users_detail = execute_query("""
                SELECT name, phone, user_type, default_location, is_active, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 20
            """)
            if not users_detail.empty:
                st.dataframe(users_detail, use_container_width=True)
            else:
                st.info("No user data available.")
        except Exception as e:
            st.error(f"Error loading user data: {e}")
    
    with tab_analytics2:
        try:
            products_detail = execute_query("""
                SELECT p.name, p.name_amharic, p.category, p.unit, p.current_price, 
                       p.quantity_available, p.expiry_date, u.name as supplier_name
                FROM products p
                JOIN users u ON p.supplier_id = u.id
                ORDER BY p.current_price DESC
                LIMIT 20
            """)
            if not products_detail.empty:
                st.dataframe(products_detail, use_container_width=True)
            else:
                st.info("No product data available.")
        except Exception as e:
            st.error(f"Error loading product data: {e}")
    
    with tab_analytics3:
        try:
            orders_detail = execute_query("""
                SELECT o.id, o.created_at, o.status, o.total_amount, o.quantity_ordered,
                       u.name as customer_name, p.name as product_name, p.unit
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN products p ON o.product_id = p.id
                ORDER BY o.created_at DESC
                LIMIT 20
            """)
            if not orders_detail.empty:
                st.dataframe(orders_detail, use_container_width=True)
            else:
                st.info("No order data available.")
        except Exception as e:
            st.error(f"Error loading order data: {e}")
    
    with tab_analytics4:
        try:
            revenue_detail = execute_query("""
                SELECT DATE(o.created_at) as date,
                       COUNT(*) as orders,
                       SUM(o.total_amount) as revenue,
                       AVG(o.total_amount) as avg_order_value
                FROM orders o
                WHERE o.created_at >= date('now', '-30 days')
                GROUP BY DATE(o.created_at)
                ORDER BY date DESC
            """)
            if not revenue_detail.empty:
                st.dataframe(revenue_detail, use_container_width=True)
            else:
                st.info("No revenue data available.")
        except Exception as e:
            st.error(f"Error loading revenue data: {e}")

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
    st.markdown('<h2 class="sub-header">🧠 Enhanced Knowledge Base</h2>', unsafe_allow_html=True)
    
    # Knowledge search with AI
    st.markdown("### 🔍 AI-Powered Knowledge Search")
    knowledge_query = st.text_input("Ask anything about products, storage, nutrition, recipes...", 
                                   placeholder="e.g., How to store tomatoes? What are the calories in bananas?")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_button = st.button("🔍 Search Knowledge", type="primary")
    
    with col2:
        if st.button("💡 Get Random Tips"):
            # Get random knowledge items
            random_knowledge = execute_query("""
                SELECT pk.id, pk.knowledge_type, pk.content, pk.language, pk.created_at,
                       p.name as product_name
                FROM product_knowledge pk
                LEFT JOIN products p ON pk.product_id = p.id
                ORDER BY RANDOM() 
                LIMIT 3
            """)
            if not random_knowledge.empty:
                st.session_state.random_tips = random_knowledge
    
    with col3:
        if st.button("🔄 Refresh Knowledge"):
            st.rerun()
    
    # Display search results
    if search_button and knowledge_query:
        try:
            # Use RAG service for semantic search
            results = rag_service.search_knowledge(
                query=knowledge_query,
                limit=10
            )
            
            if results:
                st.success(f"🤖 Found {len(results)} relevant knowledge items")
                
                for i, result in enumerate(results):
                    with st.expander(f"📚 {result.get('title', 'Knowledge Item')} #{i+1}"):
                        st.markdown(f"**Content:** {result.get('content', 'No content available')}")
                        if result.get('metadata'):
                            st.markdown(f"**Category:** {result.get('metadata', {}).get('category', 'N/A')}")
                            st.markdown(f"**Tags:** {result.get('metadata', {}).get('tags', 'N/A')}")
                        st.markdown(f"**Relevance Score:** {result.get('score', 0):.2f}")
            else:
                st.info("🤔 No specific knowledge found. Try asking about storage tips, nutritional info, or recipes!")
                
        except Exception as e:
            st.error(f"Error searching knowledge: {e}")
    
    # Display random tips if requested
    if hasattr(st.session_state, 'random_tips') and not st.session_state.random_tips.empty:
        st.markdown("### 💡 Random Knowledge Tips")
        for _, tip in st.session_state.random_tips.iterrows():
            with st.expander(f"💡 {tip['knowledge_type'].title()} #{tip['id'][:8]}"):
                st.markdown(tip['content'])
                st.markdown(f"**Product:** {tip.get('product_name', 'N/A')}")
                st.markdown(f"**Language:** {tip.get('language', 'N/A')}")
                st.markdown(f"**Type:** {tip.get('knowledge_type', 'N/A')}")
    
    # Knowledge categories
    st.markdown("### 📚 Knowledge Categories")
    
    tab_knowledge1, tab_knowledge2, tab_knowledge3, tab_knowledge4 = st.tabs([
        "🍅 Product Info", "❄️ Storage Tips", "🥗 Nutrition", "👨‍🍳 Recipes"
    ])
    
    with tab_knowledge1:
        st.markdown("#### 🍅 Product Information")
        try:
            product_info = execute_query("""
                SELECT pk.id, pk.product_id, pk.knowledge_type, pk.content, pk.language, pk.created_at,
                       p.name as product_name, p.category as product_category
                FROM product_knowledge pk
                LEFT JOIN products p ON pk.product_id = p.id
                WHERE pk.knowledge_type IN ('seasonal', 'nutrition', 'storage', 'recipe')
                ORDER BY pk.created_at DESC
                LIMIT 15
            """)
            if not product_info.empty:
                st.info(f"📚 Showing {len(product_info)} knowledge items about products")
                for _, item in product_info.iterrows():
                    with st.expander(f"📦 {item['knowledge_type'].title()} - {item.get('product_name', 'General')} #{item['id'][:8]}"):
                        st.markdown(item['content'])
                        st.markdown(f"**Product:** {item.get('product_name', 'N/A')}")
                        st.markdown(f"**Category:** {item.get('product_category', 'N/A')}")
                        st.markdown(f"**Language:** {item.get('language', 'N/A')}")
                        st.markdown(f"**Type:** {item.get('knowledge_type', 'N/A')}")
            else:
                st.info("No product information available.")
        except Exception as e:
            st.error(f"Error loading product info: {e}")
    
    with tab_knowledge2:
        st.markdown("#### ❄️ Storage Tips")
        try:
            storage_tips = execute_query("""
                SELECT pk.id, pk.product_id, pk.knowledge_type, pk.content, pk.language, pk.created_at,
                       p.name as product_name
                FROM product_knowledge pk
                LEFT JOIN products p ON pk.product_id = p.id
                WHERE pk.knowledge_type = 'storage' OR pk.content LIKE '%storage%' OR pk.content LIKE '%store%'
                ORDER BY pk.created_at DESC
                LIMIT 10
            """)
            if not storage_tips.empty:
                for _, item in storage_tips.iterrows():
                    with st.expander(f"❄️ Storage Tip #{item['id'][:8]}"):
                        st.markdown(item['content'])
                        st.markdown(f"**Product:** {item.get('product_name', 'N/A')}")
                        st.markdown(f"**Language:** {item.get('language', 'N/A')}")
                        st.markdown(f"**Type:** {item.get('knowledge_type', 'N/A')}")
            else:
                st.info("No storage tips available.")
        except Exception as e:
            st.error(f"Error loading storage tips: {e}")
    
    with tab_knowledge3:
        st.markdown("#### 🥗 Nutritional Information")
        try:
            nutrition_info = execute_query("""
                SELECT pk.id, pk.product_id, pk.knowledge_type, pk.content, pk.language, pk.created_at,
                       p.name as product_name
                FROM product_knowledge pk
                LEFT JOIN products p ON pk.product_id = p.id
                WHERE pk.knowledge_type = 'nutrition' OR pk.content LIKE '%nutrition%' OR pk.content LIKE '%calorie%' OR pk.content LIKE '%vitamin%'
                ORDER BY pk.created_at DESC
                LIMIT 10
            """)
            if not nutrition_info.empty:
                for _, item in nutrition_info.iterrows():
                    with st.expander(f"🥗 Nutrition Info #{item['id'][:8]}"):
                        st.markdown(item['content'])
                        st.markdown(f"**Product:** {item.get('product_name', 'N/A')}")
                        st.markdown(f"**Language:** {item.get('language', 'N/A')}")
                        st.markdown(f"**Type:** {item.get('knowledge_type', 'N/A')}")
            else:
                st.info("No nutritional information available.")
        except Exception as e:
            st.error(f"Error loading nutrition info: {e}")
    
    with tab_knowledge4:
        st.markdown("#### 👨‍🍳 Recipes & Cooking")
        try:
            recipes = execute_query("""
                SELECT pk.id, pk.product_id, pk.knowledge_type, pk.content, pk.language, pk.created_at,
                       p.name as product_name
                FROM product_knowledge pk
                LEFT JOIN products p ON pk.product_id = p.id
                WHERE pk.knowledge_type = 'recipe' OR pk.content LIKE '%recipe%' OR pk.content LIKE '%cook%' OR pk.content LIKE '%prepare%'
                ORDER BY pk.created_at DESC
                LIMIT 10
            """)
            if not recipes.empty:
                for _, item in recipes.iterrows():
                    with st.expander(f"👨‍🍳 Recipe #{item['id'][:8]}"):
                        st.markdown(item['content'])
                        st.markdown(f"**Product:** {item.get('product_name', 'N/A')}")
                        st.markdown(f"**Language:** {item.get('language', 'N/A')}")
                        st.markdown(f"**Type:** {item.get('knowledge_type', 'N/A')}")
            else:
                st.info("No recipes available.")
        except Exception as e:
            st.error(f"Error loading recipes: {e}")
    
    # Knowledge statistics
    st.markdown("### 📊 Knowledge Base Statistics")
    
    try:
        # Get comprehensive stats
        total_knowledge = execute_query("SELECT COUNT(*) as count FROM product_knowledge").iloc[0]['count']
        knowledge_types = execute_query("SELECT DISTINCT knowledge_type FROM product_knowledge WHERE knowledge_type IS NOT NULL")
        recent_knowledge = execute_query("SELECT COUNT(*) as count FROM product_knowledge WHERE created_at >= date('now', '-30 days')").iloc[0]['count']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Knowledge Items", f"{total_knowledge:,}")
        
        with col2:
            st.metric("Knowledge Types", f"{len(knowledge_types):,}")
        
        with col3:
            st.metric("Recent Additions", f"{recent_knowledge:,}")
        
        with col4:
            avg_length = execute_query("SELECT AVG(LENGTH(content)) as avg_length FROM product_knowledge").iloc[0]['avg_length'] or 0
            st.metric("Avg Content Length", f"{avg_length:.0f} chars")
        
        # Knowledge distribution chart
        if not knowledge_types.empty:
            knowledge_type_counts = execute_query("""
                SELECT knowledge_type, COUNT(*) as count 
                FROM product_knowledge 
                WHERE knowledge_type IS NOT NULL
                GROUP BY knowledge_type 
                ORDER BY count DESC
            """)
            
            if not knowledge_type_counts.empty:
                fig_categories = px.bar(knowledge_type_counts, x='knowledge_type', y='count',
                                      title="Knowledge Distribution by Type",
                                      color='count',
                                      color_continuous_scale='Greens')
                fig_categories.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_categories, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error getting knowledge statistics: {e}")
    
    # Quick knowledge actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌱 Seasonal Tips"):
            seasonal_query = "seasonal vegetables fruits Ethiopia"
            try:
                results = rag_service.search_knowledge(query=seasonal_query, limit=3)
                if results:
                    st.success("Found seasonal information!")
                    for result in results:
                        st.info(f"📅 {result.get('content', '')[:100]}...")
                else:
                    st.info("No seasonal tips found.")
            except Exception as e:
                st.error(f"Error searching seasonal tips: {e}")
    
    with col2:
        if st.button("💊 Health Benefits"):
            health_query = "health benefits nutrition vitamins"
            try:
                results = rag_service.search_knowledge(query=health_query, limit=3)
                if results:
                    st.success("Found health information!")
                    for result in results:
                        st.info(f"💊 {result.get('content', '')[:100]}...")
                else:
                    st.info("No health information found.")
            except Exception as e:
                st.error(f"Error searching health info: {e}")
    
    with col3:
        if st.button("🍳 Cooking Tips"):
            cooking_query = "cooking preparation recipes"
            try:
                results = rag_service.search_knowledge(query=cooking_query, limit=3)
                if results:
                    st.success("Found cooking information!")
                    for result in results:
                        st.info(f"🍳 {result.get('content', '')[:100]}...")
                else:
                    st.info("No cooking tips found.")
            except Exception as e:
                st.error(f"Error searching cooking tips: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 <strong>KcartBot</strong> - Empowering Ethiopian agriculture through AI-driven commerce!</p>
    <p>Built with ❤️ using Streamlit, Gemini AI, and modern web technologies</p>
</div>
""", unsafe_allow_html=True)
