import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .database import execute_query

def render_analytics_tab():
    """Render the analytics tab."""
    st.markdown('<h2 class="sub-header">📊 Dynamic Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Analytics", type="secondary"):
        st.rerun()
    
    try:
        # Enhanced Key metrics with trends
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = execute_query("SELECT COUNT(*) as count FROM users").iloc[0]['count']
            active_users = execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = true").iloc[0]['count']
            new_users_week = execute_query("SELECT COUNT(*) as count FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'").iloc[0]['count']
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
            recent_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'").iloc[0]['count']
            pending_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'").iloc[0]['count']
            st.metric("Total Orders", f"{total_orders:,}", f"+{recent_orders} this week")
            st.caption(f"{pending_orders} pending orders")
        
        with col4:
            total_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders").iloc[0]['total'] or 0
            weekly_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'").iloc[0]['total'] or 0
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
            orders_by_date = execute_query("""
                SELECT DATE(created_at) as date, COUNT(*) as order_count, SUM(total_amount) as total_revenue
                FROM orders 
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
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
                HAVING COUNT(o.id) > 0
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
                WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(o.created_at)
                ORDER BY date DESC
            """)
            if not revenue_detail.empty:
                st.dataframe(revenue_detail, use_container_width=True)
            else:
                st.info("No revenue data available.")
        except Exception as e:
            st.error(f"Error loading revenue data: {e}")