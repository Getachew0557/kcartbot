import streamlit as st
import pandas as pd
from datetime import datetime
from .database import execute_query

def render_products_tab():
    """Render the products tab."""
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
            WHERE p.is_active = true
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
                    if row['expiry_date'] and pd.notna(row['expiry_date']):
                        try:
                            expiry = datetime.fromisoformat(str(row['expiry_date']))
                            days_left = (expiry - datetime.now()).days
                            if days_left < 0:
                                st.error(f"Expired {abs(days_left)} days ago")
                            elif days_left <= 3:
                                st.warning(f"Expires in {days_left} days")
                            else:
                                st.success(f"Expires in {days_left} days")
                        except (ValueError, TypeError) as e:
                            st.info(f"Invalid expiry date: {row['expiry_date']}")
                    else:
                        st.info("No expiry date")
    else:
        st.info("No products found matching your criteria.")