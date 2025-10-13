from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from src.database.models import Product, CompetitorPrice, Transaction, Supplier
import random

class MCPTools:
    def __init__(self, db: Session):
        self.db = db
    
    def get_competitor_pricing(self, product_name: str):
        """Get current competitor pricing for a product"""
        try:
            # Get the product
            product = self.db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
            if not product:
                return f"Product '{product_name}' not found"
            
            # Get recent competitor prices (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            competitor_prices = self.db.query(CompetitorPrice).filter(
                CompetitorPrice.product_id == product.id,
                CompetitorPrice.date >= thirty_days_ago
            ).all()
            
            if not competitor_prices:
                return f"No recent competitor pricing data for {product_name}"
            
            # Calculate averages by market type
            prices_by_market = {}
            for price in competitor_prices:
                if price.source_market_type not in prices_by_market:
                    prices_by_market[price.source_market_type] = []
                prices_by_market[price.source_market_type].append(price.price)
            
            result = f"Current competitor pricing for {product_name}:\n"
            for market_type, prices in prices_by_market.items():
                if prices:  # Check if list is not empty
                    avg_price = sum(prices) / len(prices)
                    result += f"- {market_type}: ~{avg_price:.1f} ETB\n"
            
            # Add sales insight
            recent_sales = self.db.query(Transaction).filter(
                Transaction.product_name.ilike(f"%{product_name}%"),
                Transaction.order_date >= thirty_days_ago
            ).all()
            
            if recent_sales:
                successful_prices = [sale.price_per_unit for sale in recent_sales if sale.quantity_ordered >= 2]
                if successful_prices:
                    recommended_price = sum(successful_prices) / len(successful_prices)
                    result += f"\nBased on recent sales, {recommended_price:.1f} ETB moves stock quickly."
            
            return result
        except Exception as e:
            return f"Error getting pricing data: {str(e)}"
    
    def check_supplier_stock(self, supplier_name: str):
        """Check stock levels for a supplier"""
        try:
            supplier = self.db.query(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%")).first()
            if not supplier:
                return f"Supplier '{supplier_name}' not found"
            
            products = self.db.query(Product).filter(Product.supplier_id == supplier.id).all()
            
            if not products:
                return f"No products found for supplier {supplier_name}"
            
            result = f"Stock for supplier {supplier_name}:\n"
            for product in products:
                expiry_info = ""
                if product.expiry_date and product.expiry_date < datetime.now() + timedelta(days=3):
                    expiry_info = " (EXPIRING SOON!)"
                result += f"- {product.name}: {product.stock_quantity} {product.unit}{expiry_info}\n"
            
            return result
        except Exception as e:
            return f"Error checking stock: {str(e)}"
    
    def get_expiry_nudge(self, supplier_name: str):
        """Check for products nearing expiry and suggest flash sales"""
        try:
            supplier = self.db.query(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%")).first()
            if not supplier:
                return f"Supplier '{supplier_name}' not found"
            
            products = self.db.query(Product).filter(
                Product.supplier_id == supplier.id,
                Product.expiry_date.isnot(None),
                Product.expiry_date < datetime.now() + timedelta(days=3)
            ).all()
            
            if not products:
                return f"No products nearing expiry for {supplier_name}"
            
            result = "Flash Sale Recommendation:\n"
            for product in products:
                days_until_expiry = (product.expiry_date - datetime.now()).days
                result += f"- Your {product.name} expires in {days_until_expiry} days. Should we run a 20% flash sale to clear it?\n"
            
            return result
        except Exception as e:
            return f"Error checking expiry: {str(e)}"
    
    def get_supplier_schedule(self, supplier_name: str, date=None):
        """Get delivery schedule for a supplier"""
        try:
            supplier = self.db.query(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%")).first()
            if not supplier:
                return f"Supplier '{supplier_name}' not found"
            
            if not date:
                # This week's schedule
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
            else:
                start_date = datetime.strptime(date, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1)
            
            transactions = self.db.query(Transaction).filter(
                Transaction.supplier_id == supplier.id,
                Transaction.delivery_date >= start_date,
                Transaction.delivery_date < end_date
            ).all()
            
            if not transactions:
                return f"No deliveries scheduled for {supplier_name} in the specified period"
            
            result = f"Delivery schedule for {supplier_name}:\n"
            for transaction in transactions:
                result += f"- {transaction.delivery_date.strftime('%Y-%m-%d')}: {transaction.quantity_ordered} {transaction.unit} of {transaction.product_name} to {transaction.delivery_location}\n"
            
            return result
        except Exception as e:
            return f"Error getting schedule: {str(e)}"