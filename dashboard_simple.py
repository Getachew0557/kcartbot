"""Simplified KcartBot Dashboard - Data Visualization Focus"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import sys
import os

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
</style>
""", unsafe_allow_html=True)

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

# Main header
st.markdown('<h1 class="main-header">🌱 KcartBot Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced AI Agri-Commerce Assistant for Ethiopia</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/2E8B57/FFFFFF?text=KcartBot", width=200)
    
    st.markdown("### 🎯 Quick Stats")
    
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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🛒 Products", "📦 Orders", "🧠 Knowledge Base"])

# Analytics Tab
with tab1:
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
with tab2:
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
                        from datetime import datetime
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
with tab3:
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
with tab4:
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
                    query = """
                        SELECT pk.knowledge_type, pk.content, p.name as product_name
                        FROM product_knowledge pk
                        JOIN products p ON pk.product_id = p.id
                        WHERE pk.content LIKE ?
                    """
                    
                    if knowledge_type != "All":
                        query += f" AND pk.knowledge_type = '{knowledge_type}'"
                    
                    query += " LIMIT 10"
                    
                    results = execute_query(query, [f"%{knowledge_query}%"])
                    
                    if not results.empty:
                        st.success(f"Found {len(results)} knowledge items")
                        
                        for _, result in results.iterrows():
                            with st.expander(f"{result['knowledge_type'].title()}: {result['product_name']}"):
                                st.write(f"**Content:** {result['content']}")
                    else:
                        st.info("No knowledge found for your query.")
                        
                except Exception as e:
                    st.error(f"Error searching knowledge: {e}")
    
    # Knowledge statistics
    st.markdown("### 📊 Knowledge Statistics")
    
    try:
        knowledge_stats = execute_query("""
            SELECT knowledge_type, COUNT(*) as count 
            FROM product_knowledge 
            GROUP BY knowledge_type
        """)
        
        if not knowledge_stats.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_items = knowledge_stats['count'].sum()
                st.metric("Total Items", f"{total_items:,}")
            
            with col2:
                st.metric("Knowledge Types", len(knowledge_stats))
            
            with col3:
                languages = execute_query("SELECT COUNT(DISTINCT language) as count FROM product_knowledge").iloc[0]['count']
                st.metric("Languages", languages)
            
            # Knowledge type distribution
            fig_knowledge = px.pie(knowledge_stats, values='count', names='knowledge_type',
                                 title="Knowledge Distribution by Type")
            st.plotly_chart(fig_knowledge, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error getting knowledge stats: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 <strong>KcartBot</strong> - Empowering Ethiopian agriculture through AI-driven commerce!</p>
    <p>Built with ❤️ using Streamlit and modern web technologies</p>
</div>
""", unsafe_allow_html=True)
