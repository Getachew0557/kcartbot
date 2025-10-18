import streamlit as st
import pandas as pd
from .database import execute_query
from datetime import datetime
import plotly.express as px

def render_knowledge_tab(rag_service, chat_service):
    """Render the knowledge base tab."""
    st.markdown('<h2 class="sub-header">🧠 Enhanced Knowledge Base</h2>', unsafe_allow_html=True)
    
    # Knowledge search with AI
    st.markdown("### 🔍 AI-Powered Knowledge Search")
    knowledge_query = st.text_input("Ask anything about KcartBot, agriculture, products, or general questions...", 
                                   placeholder="e.g., Hello, What is KcartBot?, How to store tomatoes?, What are the benefits of red onions?")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_button = st.button("🔍 Search Knowledge", type="primary")
    
    with col2:
        if st.button("💡 Get Random Tips"):
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
    
    # Display search results with enhanced responses
    if search_button and knowledge_query:
        try:
            query_lower = knowledge_query.lower().strip()
            
            if query_lower in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']:
                st.success("👋 **Hello! Welcome to KcartBot!**")
                st.info("""
                **🌱 KcartBot** is your Advanced AI Agri-Commerce Assistant for Ethiopia! 
                
                I can help you with:
                - 🛒 **Product Discovery** - Find agricultural products
                - 💰 **Pricing Information** - Get current market prices
                - ❄️ **Storage Tips** - Learn how to store products properly
                - 🥗 **Nutritional Information** - Understand health benefits
                - 👨‍🍳 **Recipes** - Discover cooking ideas
                - 📦 **Order Management** - Place and track orders
                - 🌍 **Multi-language Support** - English, Amharic, Amhar-glish
                
                Ask me anything about agriculture, products, or how I can help you!
                """)
                
            elif any(word in query_lower for word in ['what is kcartbot', 'about kcartbot', 'kcartbot info', 'tell me about']):
                st.success("🤖 **About KcartBot**")
                st.info("""
                **🌱 KcartBot** is an Advanced AI Agri-Commerce Assistant designed specifically for Ethiopia's agricultural market.
                
                **🎯 Key Features:**
                - **AI-Powered Chat** - Natural conversations using Gemini 2.5 Flash
                - **Multi-language Support** - English, Amharic (አማርኛ), Amhar-glish
                - **Product Knowledge Base** - Comprehensive information about agricultural products
                - **Dynamic Pricing** - Real-time market price insights
                - **Order Management** - Complete order lifecycle management
                - **Supplier Network** - Connect with local suppliers
                - **Customer Support** - 24/7 AI assistance
                
                **🌍 Focus Areas:**
                - Horticulture products (fruits, vegetables)
                - Dairy products
                - Storage and preservation tips
                - Nutritional information
                - Seasonal availability
                - Ethiopian market insights
                
                **💡 How to Use:**
                - Ask questions about products
                - Get storage and cooking tips
                - Check prices and availability
                - Place orders
                - Learn about nutrition and health benefits
                """)
                
            elif any(word in query_lower for word in ['help', 'how to use', 'commands', 'what can you do']):
                st.success("🆘 **How to Use KcartBot**")
                st.info("""
                **📋 Available Commands & Questions:**
                
                **🛒 Product Queries:**
                - "Show me available products"
                - "What products are in season?"
                - "Tell me about tomatoes"
                - "What's the price of red onions?"
                
                **❄️ Storage & Preservation:**
                - "How to store tomatoes?"
                - "Best way to preserve vegetables"
                - "Storage tips for dairy products"
                
                **🥗 Nutrition & Health:**
                - "Nutritional benefits of carrots"
                - "Calories in bananas"
                - "Vitamins in spinach"
                
                **👨‍🍳 Cooking & Recipes:**
                - "Tomato recipes"
                - "How to cook Ethiopian vegetables"
                - "Traditional cooking methods"
                
                **📊 General Information:**
                - "Market trends"
                - "Seasonal availability"
                - "Supplier information"
                
                **🌍 Language Support:**
                - Switch between English, Amharic, and Amhar-glish
                - Ask questions in any supported language
                """)
                
            elif any(word in query_lower for word in ['features', 'capabilities', 'what can', 'services']):
                st.success("⚡ **KcartBot Capabilities**")
                st.info("""
                **🚀 Core Services:**
                
                **1. 🛒 Product Management**
                - Browse 15+ agricultural products
                - Real-time inventory tracking
                - Price monitoring and alerts
                - Product availability status
                
                **2. 💬 AI Chat Assistant**
                - Natural language processing
                - Multi-turn conversations
                - Context-aware responses
                - Tool-calling integration
                
                **3. 📚 Knowledge Base**
                - 84+ knowledge items
                - Storage tips and methods
                - Nutritional information
                - Recipe suggestions
                - Seasonal guidance
                
                **4. 📊 Analytics Dashboard**
                - Real-time business metrics
                - User and order analytics
                - Revenue tracking
                - Supplier performance
                
                **5. 🌍 Multi-language Support**
                - English (primary)
                - Amharic (አማርኛ)
                - Amhar-glish (mixed)
                - Automatic language detection
                
                **6. 🔧 Advanced Features**
                - MCP (Model Context Protocol) integration
                - RAG (Retrieval-Augmented Generation)
                - Vector database for semantic search
                - Real-time data synchronization
                """)
                
            elif any(word in query_lower for word in ['contact', 'support', 'help desk', 'customer service']):
                st.success("📞 **Support & Contact**")
                st.info("""
                **🆘 Getting Help:**
                
                **💬 Chat Support:**
                - Use the chat interface for immediate assistance
                - AI-powered responses 24/7
                - Context-aware help based on your questions
                
                **📚 Self-Service:**
                - Browse the Knowledge Base for common questions
                - Use the search function to find specific information
                - Check the Analytics dashboard for system status
                
                **🔍 Common Issues:**
                - **Login Problems:** Check your credentials and try refreshing
                - **Order Issues:** Use the Orders tab to track and manage orders
                - **Product Questions:** Search the Knowledge Base or ask in chat
                - **Technical Issues:** Try refreshing the page or clearing browser cache
                
                **📋 Quick Actions:**
                - Click "Get Random Tips" for helpful information
                - Use the refresh buttons to get latest data
                - Switch languages using the sidebar dropdown
                - Check the sidebar for real-time statistics
                
                **🌱 Remember:** KcartBot is designed to be your comprehensive agricultural assistant!
                """)
                
            elif any(word in query_lower for word in ['thank', 'thanks', 'appreciate']):
                st.success("🙏 **You're Welcome!**")
                st.info("""
                **😊 Thank you for using KcartBot!**
                
                I'm here to help you with all your agricultural needs. Whether you're:
                - 🛒 Looking for products
                - 📚 Learning about storage and nutrition
                - 👨‍🍳 Finding recipes
                - 📊 Checking analytics
                - 💬 Having conversations
                
                Feel free to ask me anything anytime! I'm always ready to assist you with Ethiopia's agricultural commerce.
                
                **🌱 Happy farming and shopping!**
                """)
                
            else:
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
                    st.info("🤔 No specific knowledge found. Try asking about:")
                    st.markdown("""
                    - **Products:** "Tell me about [product name]"
                    - **Storage:** "How to store [product]"
                    - **Nutrition:** "Benefits of [product]"
                    - **Recipes:** "[Product] recipes"
                    - **General:** "Hello", "What is KcartBot?", "Help"
                    """)
                
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
    
    tab_knowledge1, tab_knowledge2, tab_knowledge3, tab_knowledge4, tab_knowledge5 = st.tabs([
        "🍅 Product Info", "❄️ Storage Tips", "🥗 Nutrition", "👨‍🍳 Recipes", "🌱 General Info"
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
    
    with tab_knowledge5:
        st.markdown("#### 🌱 General Information")
        
        st.markdown("**🤖 About KcartBot System**")
        st.info("""
        **KcartBot** is an Advanced AI Agri-Commerce Assistant designed specifically for Ethiopia's agricultural market. 
        Built with modern AI technologies including Gemini 2.5 Flash, MCP (Model Context Protocol), and RAG (Retrieval-Augmented Generation).
        """)
        
        st.markdown("**📊 System Statistics**")
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_users = execute_query("SELECT COUNT(*) as count FROM users").iloc[0]['count']
                st.metric("Total Users", f"{total_users:,}")
            
            with col2:
                total_products = execute_query("SELECT COUNT(*) as count FROM products").iloc[0]['count']
                st.metric("Products Available", f"{total_products:,}")
            
            with col3:
                total_knowledge = execute_query("SELECT COUNT(*) as count FROM product_knowledge").iloc[0]['count']
                st.metric("Knowledge Items", f"{total_knowledge:,}")
        except Exception as e:
            st.error(f"Error loading system stats: {e}")
        
        st.markdown("**⚡ Key Features**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🛒 Product Management**
            - Real-time inventory tracking
            - Dynamic pricing updates
            - Supplier network integration
            - Product availability status
            
            **💬 AI Chat Assistant**
            - Natural language processing
            - Multi-turn conversations
            - Context-aware responses
            - Tool-calling integration
            """)
        
        with col2:
            st.markdown("""
            **📚 Knowledge Base**
            - Storage tips and methods
            - Nutritional information
            - Recipe suggestions
            - Seasonal guidance
            
            **🌍 Multi-language Support**
            - English (primary)
            - Amharic (አማርኛ)
            - Amhar-glish (mixed)
            - Automatic detection
            """)
        
        st.markdown("**🔧 Technology Stack**")
        st.markdown("""
        - **AI Model:** Gemini 2.5 Flash
        - **Framework:** Model Context Protocol (MCP)
        - **Database:** SQLite (relational) + ChromaDB (vector)
        - **Backend:** FastAPI
        - **Frontend:** Streamlit
        - **Languages:** Python, SQL
        - **Features:** RAG, Semantic Search, Real-time Analytics
        """)
        
        st.markdown("**🆘 Quick Help**")
        st.markdown("""
        **Common Questions:**
        - Type "Hello" for a welcome message
        - Ask "What is KcartBot?" for detailed information
        - Use "Help" to see available commands
        - Search for specific products or topics
        
        **Navigation:**
        - Use tabs to explore different sections
        - Click refresh buttons for latest data
        - Use sidebar for quick statistics
        - Switch languages as needed
        """)
        
        st.markdown("**📞 Support**")
        st.info("""
        **Need Help?**
        - Use the chat interface for immediate assistance
        - Browse the Knowledge Base for common questions
        - Check the Analytics dashboard for system status
        - Try the random tips feature for helpful information
        
        **Remember:** KcartBot is your comprehensive agricultural assistant!
        """)
    
    st.markdown("### 📊 Knowledge Base Statistics")
    
    try:
        total_knowledge = execute_query("SELECT COUNT(*) as count FROM product_knowledge").iloc[0]['count']
        knowledge_types = execute_query("SELECT DISTINCT knowledge_type FROM product_knowledge WHERE knowledge_type IS NOT NULL")
        recent_knowledge = execute_query("SELECT COUNT(*) as count FROM product_knowledge WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'").iloc[0]['count']
        
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