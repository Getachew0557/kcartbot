import streamlit as st
import pandas as pd
from .database import execute_query

def render_orders_tab():
    """Render the orders tab."""
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
                query += " AND DATE(o.created_at) = CURRENT_DATE"
            elif days_filter == "Last 7 days":
                query += " AND o.created_at >= CURRENT_DATE - INTERVAL '7 days'"
            elif days_filter == "Last 30 days":
                query += " AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'"
        
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
                    st.write(f"**Date:** {row['created_at'] if pd.notna(row['created_at']) else 'N/A'}")
    else:
        st.info("No orders found matching your criteria.")