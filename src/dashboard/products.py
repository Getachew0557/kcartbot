import streamlit as st
import pandas as pd
from datetime import datetime
from .database import execute_query
import os
import base64

# Add image generation import
try:
    from src.image_generation import image_generator
except ImportError:
    st.warning("Image generation service not available")
    image_generator = None

def render_products_tab():
    """Render the products tab with image generation and product management."""
    st.markdown('<h2 class="sub-header">🛒 Product Management</h2>', unsafe_allow_html=True)
    
    # Product image generation section
    if image_generator:
        st.markdown("### 🎨 AI Product Image Generation")
        
        col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
        
        with col_gen1:
            generate_product = st.selectbox(
                "Select product to generate image",
                ["Tomato", "Red Onion", "Potato", "Avocado", "Banana", "Milk", 
                 "Cabbage", "Carrot", "Ethiopian Coffee", "Ayib", "Mango", "Papaya"],
                index=0,
                key="image_product_select"
            )
        
        with col_gen2:
            generate_style = st.selectbox(
                "Style",
                ["Realistic", "Artistic", "Professional"],
                index=0,
                key="image_style_select"
            )
        
        with col_gen3:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("🔄 Generate Product Image", type="primary", key="generate_image_btn"):
                with st.spinner(f"🎨 Generating {generate_style.lower()} image for {generate_product}..."):
                    try:
                        result = image_generator.generate_product_image(
                            generate_product, 
                            style=generate_style.lower()
                        )
                        
                        if result["success"]:
                            st.session_state.generated_image = result
                            st.session_state.generated_product = generate_product
                            st.session_state.generated_style = generate_style
                            st.success(f"✅ {generate_style} image generated for {generate_product}!")
                        else:
                            st.error(f"❌ Failed to generate image: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Image generation error: {e}")
        
        # Display generated image
        if hasattr(st.session_state, 'generated_image') and st.session_state.generated_image["success"]:
            st.markdown(f"### 🖼️ Generated Image: {st.session_state.generated_product}")
            
            # Create two columns for image display and info
            col_display, col_info = st.columns([2, 1])
            
            with col_display:
                # Display the image prominently
                image_data = st.session_state.generated_image["image_data"]
                image_url = f"data:image/png;base64,{image_data}"
                
                # Display image with nice styling
                st.image(
                    image_url, 
                    width=400, 
                    caption=f"{st.session_state.generated_style} AI Generated: {st.session_state.generated_product}",
                    use_column_width=True
                )
                
                # Image status indicator
                if st.session_state.generated_image.get('is_ai_generated'):
                    st.success("🎯 **AI-Generated Photorealistic Image**")
                    st.info("This image was generated using AI based on your product description")
                elif st.session_state.generated_image.get('is_placeholder'):
                    st.info("🖼️ **Professional Placeholder Image**")
                    st.warning("Enable AI APIs in your .env file for photorealistic AI-generated images")
                
            with col_info:
                st.markdown("**📊 Image Details**")
                st.write(f"**Product:** {st.session_state.generated_product}")
                st.write(f"**Style:** {st.session_state.generated_style}")
                st.write(f"**API Used:** {st.session_state.generated_image['api_used'].title()}")
                
                if st.session_state.generated_image.get('model'):
                    st.write(f"**AI Model:** {st.session_state.generated_image['model']}")
                
                st.write(f"**Generated:** {st.session_state.generated_image['timestamp'][11:19]}")
                st.write(f"**Image ID:** {st.session_state.generated_image['image_id'][:8]}...")
                
                # Download section
                st.markdown("---")
                st.markdown("**💾 Download Options**")
                
                if st.button("📥 Download PNG Image", key="download_btn"):
                    try:
                        # Save image to file
                        filename = f"{st.session_state.generated_product.lower().replace(' ', '_')}_{st.session_state.generated_style.lower()}.png"
                        filepath = os.path.join("data/generated_images", filename)
                        os.makedirs("data/generated_images", exist_ok=True)
                        
                        with open(filepath, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                        
                        st.success(f"✅ Image saved to: `{filepath}`")
                        
                        # Provide download link
                        with open(filepath, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Now",
                                data=file,
                                file_name=filename,
                                mime="image/png",
                                key="download_now_btn"
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to save image: {e}")
                
                # Regenerate button
                if st.button("🔄 Generate New Version", key="regenerate_btn"):
                    # Clear current image to trigger regeneration
                    del st.session_state.generated_image
                    st.rerun()
    
    # Product search and display section
    st.markdown("### 🔍 Product Search & Inventory")
    
    # Search and filter controls
    col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
    
    with col_search1:
        search_query = st.text_input(
            "🔍 Search Products by name", 
            placeholder="Enter product name...", 
            key="product_search_main"
        )
    
    with col_search2:
        category_filter = st.selectbox(
            "Filter by Category", 
            ["All", "horticulture", "dairy"], 
            key="category_filter_main"
        )
    
    with col_search3:
        sort_by = st.selectbox(
            "Sort by", 
            ["name", "current_price", "quantity_available"], 
            key="sort_by_main"
        )
    
    # Quick actions row
    col_actions1, col_actions2, col_actions3, col_actions4 = st.columns(4)
    
    with col_actions1:
        if st.button("📊 Refresh Products", key="refresh_products"):
            st.rerun()
    
    with col_actions2:
        if st.button("🔄 Generate All Images", key="generate_all_images"):
            st.info("This would generate images for all products (batch processing)")
    
    with col_actions3:
        if st.button("📋 Export Product List", key="export_products"):
            st.info("Product list export feature would be implemented here")
    
    with col_actions4:
        show_images = st.checkbox("🖼️ Show Product Images", value=True, key="show_images_checkbox")
    
    try:
        # Get products from database
        query = """
            SELECT p.id, p.name, p.name_amharic, p.category, p.unit, p.current_price, 
                   p.quantity_available, p.expiry_date, p.description,
                   u.name as supplier_name, u.phone as supplier_phone
            FROM products p
            JOIN users u ON p.supplier_id = u.id
            WHERE p.is_active = true
        """
        
        if search_query:
            query += f" AND (p.name ILIKE '%{search_query}%' OR p.name_amharic ILIKE '%{search_query}%')"
        
        if category_filter != "All":
            query += f" AND p.category = '{category_filter}'"
        
        query += f" ORDER BY p.{sort_by} DESC"
        
        products_df = execute_query(query)
    except Exception as e:
        st.error(f"❌ Error loading products: {e}")
        products_df = pd.DataFrame()
    
    # Display products
    if not products_df.empty:
        st.markdown(f"#### 📦 Found {len(products_df)} Products")
        
        # Create a grid layout for products
        for idx, row in products_df.iterrows():
            # Create a unique key for each product card
            product_key = f"product_card_{idx}_{row['name'].replace(' ', '_').lower()}"
            
            # Create expandable product card
            with st.expander(f"🛒 {row['name']} - ETB {row['current_price']:.2f}/{row['unit']}", expanded=False):
                
                # Main product layout - Image on left, details on right
                col_left, col_right = st.columns([1, 2])
                
                with col_left:
                    # Product Image Section
                    st.markdown("**🖼️ Product Image**")
                    
                    # Check if we should show images
                    if show_images and image_generator:
                        # Try to generate or show image for this product
                        image_key = f"product_image_{idx}"
                        
                        if image_key not in st.session_state:
                            # Generate image on first view
                            with st.spinner("Generating image..."):
                                try:
                                    img_result = image_generator.generate_product_image(row['name'])
                                    st.session_state[image_key] = img_result
                                except Exception as e:
                                    st.session_state[image_key] = None
                        
                        # Display the image
                        if st.session_state.get(image_key) and st.session_state[image_key]["success"]:
                            img_data = st.session_state[image_key]["image_data"]
                            img_url = f"data:image/png;base64,{img_data}"
                            st.image(img_url, width=200, use_column_width=True)
                            
                            # Quick regenerate button for this product
                            if st.button("🔄 Regenerate", key=f"regen_{idx}"):
                                del st.session_state[image_key]
                                st.rerun()
                        else:
                            st.info("🖼️ No image available")
                    
                    # Quick image generation button
                    if image_generator and st.button(f"🎨 Generate Image", key=f"quick_gen_{idx}"):
                        with st.spinner(f"Generating image for {row['name']}..."):
                            try:
                                quick_result = image_generator.generate_product_image(row['name'])
                                if quick_result["success"]:
                                    st.session_state[image_key] = quick_result
                                    st.success("✅ Image generated!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Generation failed: {e}")
                
                with col_right:
                    # Product Details Section
                    col_detail1, col_detail2 = st.columns(2)
                    
                    with col_detail1:
                        st.markdown("**📋 Product Details**")
                        st.write(f"**Category:** {row['category'].title()}")
                        st.write(f"**Supplier:** {row['supplier_name']}")
                        st.write(f"**Contact:** {row['supplier_phone']}")
                        st.write(f"**Unit:** {row['unit']}")
                        
                        # Amharic name if available
                        if row['name_amharic'] and pd.notna(row['name_amharic']):
                            st.write(f"**Amharic:** {row['name_amharic']}")
                    
                    with col_detail2:
                        st.markdown("**💰 Pricing & Stock**")
                        st.write(f"**Price:** ETB {row['current_price']:.2f}")
                        st.write(f"**Available:** {row['quantity_available']:.1f} {row['unit']}")
                        
                        # Stock status with color coding
                        if row['quantity_available'] > 10:
                            st.success("✅ In Stock")
                        elif row['quantity_available'] > 0:
                            st.warning("⚠️ Low Stock")
                        else:
                            st.error("❌ Out of Stock")
                        
                        # Expiry date information
                        if row['expiry_date'] and pd.notna(row['expiry_date']):
                            try:
                                expiry = datetime.fromisoformat(str(row['expiry_date']))
                                days_left = (expiry - datetime.now()).days
                                if days_left < 0:
                                    st.error(f"❌ Expired {abs(days_left)} days ago")
                                elif days_left <= 3:
                                    st.warning(f"⚠️ Expires in {days_left} days")
                                elif days_left <= 7:
                                    st.info(f"ℹ️ Expires in {days_left} days")
                                else:
                                    st.success(f"✅ Expires in {days_left} days")
                            except (ValueError, TypeError):
                                st.info(f"📅 Expiry: {row['expiry_date']}")
                        else:
                            st.info("📅 No expiry date")
                    
                    # Product description
                    if row['description'] and pd.notna(row['description']):
                        st.markdown("**📝 Description**")
                        st.write(row['description'])
                
                # Action buttons row
                st.markdown("---")
                col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                
                with col_btn1:
                    if st.button("💬 Chat About", key=f"chat_btn_{idx}"):
                        # Pre-fill chat with product query
                        st.session_state.chat_input = f"Tell me about {row['name']} - price, storage, nutrition, recipes"
                        # Switch to chat tab
                        st.session_state.active_tab = "💬 Chat Interface"
                        st.rerun()
                
                with col_btn2:
                    if st.button("📊 View Analytics", key=f"analytics_btn_{idx}"):
                        st.info(f"📈 Analytics for {row['name']}:")
                        st.write(f"- Price: ETB {row['current_price']:.2f}")
                        st.write(f"- Stock: {row['quantity_available']} {row['unit']}")
                        st.write(f"- Category: {row['category']}")
                
                with col_btn3:
                    if st.button("🛒 Quick Order", key=f"order_btn_{idx}"):
                        if row['quantity_available'] > 0:
                            st.success(f"✅ {row['name']} added to cart!")
                            st.write(f"Price: ETB {row['current_price']:.2f} per {row['unit']}")
                            
                            # Quantity selector
                            quantity = st.number_input(
                                f"Quantity ({row['unit']})", 
                                min_value=0.1, 
                                max_value=float(row['quantity_available']), 
                                value=1.0,
                                key=f"qty_{idx}"
                            )
                            
                            if st.button("✅ Confirm Order", key=f"confirm_{idx}"):
                                total = quantity * row['current_price']
                                st.success(f"🎉 Order confirmed! {quantity} {row['unit']} of {row['name']} - ETB {total:.2f}")
                        else:
                            st.error("❌ Product out of stock")
                
                with col_btn4:
                    if image_generator and st.button("🎨 Featured Image", key=f"feature_{idx}"):
                        # Set this product as the featured image generation
                        st.session_state.generated_product = row['name']
                        st.session_state.generated_image = None  # Clear to trigger regeneration
                        st.success(f"🎯 {row['name']} selected for image generation!")
                        st.rerun()
    
    else:
        # No products found
        st.info("📭 No products found matching your criteria.")
        
        # Helpful suggestions
        st.markdown("**💡 Try these:**")
        st.markdown("""
        - Clear your search filters
        - Check different categories
        - Make sure products are active in the database
        - Try searching with different keywords
        """)
    
    # Batch image generation section
    if image_generator and st.checkbox("🚀 Show Batch Image Generation", key="batch_toggle"):
        st.markdown("### 🚀 Batch Image Generation")
        
        col_batch1, col_batch2 = st.columns(2)
        
        with col_batch1:
            selected_products = st.multiselect(
                "Select products for batch generation",
                ["Tomato", "Red Onion", "Potato", "Avocado", "Banana", "Milk", 
                 "Cabbage", "Carrot", "Ethiopian Coffee", "Ayib", "Mango", "Papaya"],
                default=["Tomato", "Banana", "Carrot"],
                key="batch_products"
            )
        
        with col_batch2:
            batch_style = st.selectbox(
                "Batch Style",
                ["Realistic", "Professional", "Artistic"],
                key="batch_style"
            )
            
            if st.button("🔄 Generate Batch Images", key="batch_generate_btn"):
                if selected_products:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    generated_count = 0
                    for i, product in enumerate(selected_products):
                        status_text.text(f"🔄 Generating {product}... ({i+1}/{len(selected_products)})")
                        
                        try:
                            result = image_generator.generate_product_image(product, style=batch_style.lower())
                            if result["success"]:
                                generated_count += 1
                                st.success(f"✅ {product}: Generated successfully")
                            else:
                                st.warning(f"⚠️ {product}: {result.get('error', 'Failed')}")
                        except Exception as e:
                            st.error(f"❌ {product}: {e}")
                        
                        progress_bar.progress((i + 1) / len(selected_products))
                    
                    status_text.text(f"🎉 Batch complete! {generated_count}/{len(selected_products)} images generated")
                    progress_bar.empty()
                else:
                    st.warning("⚠️ Please select at least one product for batch generation")