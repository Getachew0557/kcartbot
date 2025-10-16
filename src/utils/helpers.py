"""Helper utilities for KcartBot."""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def hash_phone(phone: str) -> str:
    """Hash phone number for privacy."""
    return hashlib.sha256(phone.encode()).hexdigest()[:16]


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Ethiopian phone number patterns
    patterns = [
        r'^\+251[0-9]{9}$',  # +251XXXXXXXXX
        r'^0[0-9]{9}$',      # 0XXXXXXXXX
        r'^251[0-9]{9}$'     # 251XXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False


def format_phone(phone: str) -> str:
    """Format phone number to standard format."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if len(digits) == 10 and digits.startswith('0'):
        return f"+251{digits[1:]}"
    elif len(digits) == 12 and digits.startswith('251'):
        return f"+{digits}"
    elif len(digits) == 13 and digits.startswith('251'):
        return f"+{digits}"
    
    return phone


def calculate_delivery_date(days_ahead: int = 1) -> datetime:
    """Calculate delivery date."""
    return datetime.utcnow() + timedelta(days=days_ahead)


def format_currency(amount: float, currency: str = "ETB") -> str:
    """Format currency amount."""
    return f"{amount:.2f} {currency}"


def calculate_order_total(quantity: float, unit_price: float) -> float:
    """Calculate order total."""
    return round(quantity * unit_price, 2)


def is_expiring_soon(expiry_date: datetime, days_threshold: int = 3) -> bool:
    """Check if product is expiring soon."""
    if not expiry_date:
        return False
    
    threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
    return expiry_date <= threshold_date


def get_expiry_status(expiry_date: datetime) -> str:
    """Get expiry status description."""
    if not expiry_date:
        return "No expiry date"
    
    now = datetime.utcnow()
    days_left = (expiry_date - now).days
    
    if days_left < 0:
        return "Expired"
    elif days_left == 0:
        return "Expires today"
    elif days_left <= 3:
        return f"Expires in {days_left} days"
    else:
        return f"Expires in {days_left} days"


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    return text[:500].strip()


def extract_quantity_from_text(text: str) -> Optional[float]:
    """Extract quantity from text."""
    # Look for patterns like "5kg", "2 liters", "10", etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram|kilo)',
        r'(\d+(?:\.\d+)?)\s*(?:liter|litre|l)',
        r'(\d+(?:\.\d+)?)\s*(?:piece|pcs|p)',
        r'(\d+(?:\.\d+)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    
    return None


def extract_product_name_from_text(text: str, available_products: List[str]) -> Optional[str]:
    """Extract product name from text."""
    text_lower = text.lower()
    
    for product in available_products:
        product_lower = product.lower()
        if product_lower in text_lower:
            return product
    
    return None


def format_delivery_time(delivery_date: datetime) -> str:
    """Format delivery date for display."""
    now = datetime.utcnow()
    days_diff = (delivery_date - now).days
    
    if days_diff == 0:
        return "Today"
    elif days_diff == 1:
        return "Tomorrow"
    elif days_diff <= 7:
        return f"In {days_diff} days"
    else:
        return delivery_date.strftime("%B %d, %Y")


def get_seasonal_recommendation(month: int) -> str:
    """Get seasonal recommendation based on month."""
    recommendations = {
        1: "Dry season - Good for root vegetables and citrus fruits",
        2: "Dry season - Ideal for leafy greens and tomatoes",
        3: "Transition period - Fresh produce availability varies",
        4: "Rainy season begins - Limited fresh produce",
        5: "Rainy season - Focus on stored products",
        6: "Rainy season - Limited availability",
        7: "Rainy season - Plan ahead for fresh produce",
        8: "Rainy season - Consider preserved products",
        9: "Transition period - Fresh produce returns",
        10: "Dry season begins - Abundant fresh produce",
        11: "Dry season - Peak season for most products",
        12: "Dry season - Holiday season, high demand"
    }
    
    return recommendations.get(month, "Seasonal availability varies")


def create_order_summary(order_data: Dict[str, Any]) -> str:
    """Create order summary text."""
    product_name = order_data.get("product_name", "Unknown Product")
    quantity = order_data.get("quantity", 0)
    unit = order_data.get("unit", "kg")
    total_amount = order_data.get("total_amount", 0)
    delivery_date = order_data.get("delivery_date")
    
    summary = f"Order Summary:\n"
    summary += f"Product: {product_name}\n"
    summary += f"Quantity: {quantity} {unit}\n"
    summary += f"Total: {format_currency(total_amount)}\n"
    
    if delivery_date:
        summary += f"Delivery: {format_delivery_time(delivery_date)}\n"
    
    summary += f"Payment: Cash on Delivery"
    
    return summary


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_order_reference() -> str:
    """Generate order reference number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"KC{timestamp}{random_suffix}"


def parse_delivery_location(location: str) -> Dict[str, str]:
    """Parse delivery location into components."""
    # Simple parsing - in production, use geocoding service
    parts = location.split(',')
    
    return {
        "city": parts[0].strip() if len(parts) > 0 else "",
        "area": parts[1].strip() if len(parts) > 1 else "",
        "full_address": location.strip()
    }


def calculate_delivery_fee(distance_km: float, base_fee: float = 50) -> float:
    """Calculate delivery fee based on distance."""
    if distance_km <= 5:
        return base_fee
    elif distance_km <= 10:
        return base_fee + 25
    elif distance_km <= 20:
        return base_fee + 50
    else:
        return base_fee + 100


def get_product_category_emoji(category: str) -> str:
    """Get emoji for product category."""
    emojis = {
        "horticulture": "🥬",
        "dairy": "🥛",
        "fruits": "🍎",
        "vegetables": "🥕"
    }
    return emojis.get(category.lower(), "📦")


def format_product_list(products: List[Dict[str, Any]]) -> str:
    """Format product list for display."""
    if not products:
        return "No products found."
    
    formatted = "Available Products:\n"
    for i, product in enumerate(products, 1):
        name = product.get("name", "Unknown")
        price = product.get("current_price", 0)
        unit = product.get("unit", "kg")
        available = product.get("quantity_available", 0)
        
        formatted += f"{i}. {name} - {format_currency(price)}/{unit} (Available: {available} {unit})\n"
    
    return formatted

