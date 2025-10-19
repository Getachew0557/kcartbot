"""
Image Generation Service for KcartBot Dashboard
Integrated with Hugging Face API for product images
"""

import os
import base64
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import io
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardImageGenerator:
    """Image generation service for KcartBot dashboard."""
    
    def __init__(self):
        """Initialize image generator."""
        self.supported_apis = ["huggingface", "placeholder"]
        self.current_api = "huggingface"
        self.huggingface_models = [
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1"
        ]
        self.current_model_index = 0
        
    def generate_product_image(
        self, 
        product_name: str,
        product_description: str = "",
        style: str = "photorealistic",
        size: str = "512x512"
    ) -> Dict[str, Any]:
        """
        Generate product image for dashboard display.
        """
        try:
            prompt = self._build_dashboard_prompt(product_name, product_description, style)
            
            if self.current_api == "huggingface":
                return self._generate_with_huggingface(prompt, size)
            else:
                return self._generate_dashboard_fallback(product_name)
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return self._generate_dashboard_fallback(product_name)
    
    def _build_dashboard_prompt(self, product_name: str, description: str, style: str) -> str:
        """Build prompts optimized for dashboard display."""
        
        product_prompts = {
            "tomato": "fresh ripe tomato, red color, vegetable, food photography, natural lighting, high detail, sharp focus, clean background",
            "red onion": "fresh red onion, purple skin, whole vegetable, market, natural light, detailed, clean composition",
            "potato": "fresh potato, brown skin, whole vegetable, natural lighting, food photo, simple background",
            "avocado": "fresh avocado, green skin, healthy food, natural light, clean presentation",
            "banana": "fresh banana, yellow fruit, bunch, natural lighting, food photography, bright",
            "milk": "fresh milk, white liquid, dairy, natural light, clean, professional",
            "cabbage": "fresh cabbage, green leaves, whole vegetable, natural lighting, crisp",
            "carrot": "fresh carrot, orange vegetable, natural light, vibrant colors",
            "coffee": "coffee beans, dark roast, natural lighting, detailed, aromatic",
            "ayib": "white cheese, crumbly texture, traditional, food photography, clean",
            "mango": "fresh mango, yellow fruit, tropical, natural light, juicy",
            "papaya": "fresh papaya, tropical fruit, natural lighting, vibrant"
        }
        
        product_lower = product_name.lower()
        for key, prompt in product_prompts.items():
            if key in product_lower:
                return prompt
        
        return f"fresh {product_name}, food photography, natural lighting, high detail, clean background"
    
    def _generate_with_huggingface(self, prompt: str, size: str) -> Dict[str, Any]:
        """Generate image using Hugging Face API."""
        try:
            huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
            
            if not huggingface_token or huggingface_token.startswith("your_"):
                logger.warning("No valid Hugging Face token provided")
                raise Exception("Please set HUGGINGFACE_TOKEN in your .env file")
            
            model = self.huggingface_models[self.current_model_index]
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {huggingface_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Generating dashboard image: {prompt}")
            
            payload = {
                "inputs": prompt,
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }
            
            response = requests.post(
                API_URL, 
                headers=headers, 
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                # Process and optimize image for dashboard
                image = Image.open(io.BytesIO(response.content))
                
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize for dashboard display
                image = image.resize((400, 300), Image.Resampling.LANCZOS)
                
                # Convert to base64 for web display
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG', optimize=True)
                img_byte_arr = img_byte_arr.getvalue()
                
                image_data = base64.b64encode(img_byte_arr).decode('utf-8')
                
                return {
                    "success": True,
                    "image_data": image_data,
                    "image_url": None,
                    "api_used": "huggingface",
                    "model": model,
                    "prompt": prompt,
                    "timestamp": datetime.now().isoformat(),
                    "image_id": str(uuid.uuid4()),
                    "is_ai_generated": True
                }
                
            elif response.status_code == 503:
                logger.warning(f"Model {model} is loading")
                self._switch_to_next_model()
                return self._generate_with_huggingface(prompt, size)
                
            else:
                error_msg = f"Hugging Face API error {response.status_code}"
                logger.error(error_msg)
                
                if self.current_model_index < len(self.huggingface_models) - 1:
                    self._switch_to_next_model()
                    return self._generate_with_huggingface(prompt, size)
                else:
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.warning(f"Hugging Face generation failed: {e}")
            raise
    
    def _switch_to_next_model(self):
        """Switch to the next available model."""
        self.current_model_index = (self.current_model_index + 1) % len(self.huggingface_models)
        logger.info(f"Switched to model: {self.huggingface_models[self.current_model_index]}")
    
    def _generate_dashboard_fallback(self, product_name: str) -> Dict[str, Any]:
        """Generate a dashboard-optimized fallback image."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create dashboard-optimized image
            width, height = 400, 300
            image = Image.new('RGB', (width, height), color=(245, 245, 245))
            draw = ImageDraw.Draw(image)
            
            # Professional color scheme
            product_colors = {
                "tomato": (220, 60, 50),
                "red onion": (150, 40, 60),
                "potato": (180, 140, 100),
                "avocado": (80, 130, 60),
                "banana": (240, 220, 80),
                "milk": (250, 250, 255),
                "cabbage": (120, 170, 100),
                "carrot": (240, 140, 40),
                "coffee": (100, 70, 40),
                "ayib": (245, 240, 220),
                "mango": (255, 160, 60),
                "papaya": (255, 200, 140)
            }
            
            color = product_colors.get(product_name.lower(), (60, 180, 120))
            
            # Draw product illustration
            self._draw_dashboard_product(draw, product_name, color, width, height)
            
            # Add text
            self._add_dashboard_text(draw, product_name, width, height)
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            image_data = base64.b64encode(img_byte_arr).decode('utf-8')
            
            return {
                "success": True,
                "image_data": image_data,
                "image_url": None,
                "api_used": "dashboard_fallback",
                "prompt": f"Dashboard placeholder: {product_name}",
                "timestamp": datetime.now().isoformat(),
                "image_id": str(uuid.uuid4()),
                "is_placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Dashboard fallback failed: {e}")
            return self._create_basic_image(product_name)
    
    def _draw_dashboard_product(self, draw, product_name: str, color: tuple, width: int, height: int):
        """Draw product illustration for dashboard."""
        center_x, center_y = width // 2, height // 2 - 20
        
        if "tomato" in product_name.lower():
            draw.ellipse([center_x-50, center_y-50, center_x+50, center_y+50], fill=color)
            draw.ellipse([center_x-15, center_y-70, center_x+15, center_y-40], fill=(80, 120, 60))
        elif "banana" in product_name.lower():
            points = [
                (center_x-40, center_y-20),
                (center_x+40, center_y-40),
                (center_x+30, center_y+40),
                (center_x-30, center_y+20)
            ]
            draw.polygon(points, fill=color)
        elif "carrot" in product_name.lower():
            draw.ellipse([center_x-20, center_y-60, center_x+20, center_y+60], fill=color)
            draw.ellipse([center_x-10, center_y-80, center_x+10, center_y-60], fill=(80, 140, 60))
        else:
            draw.ellipse([center_x-50, center_y-50, center_x+50, center_y+50], fill=color)
    
    def _add_dashboard_text(self, draw, product_name: str, width: int, height: int):
        """Add text to dashboard image."""
        try:
            # Try to use system font
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Product name
            bbox = draw.textbbox((0, 0), product_name, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, height - 50), product_name, fill=(40, 40, 40), font=font)
            
            # KcartBot branding
            brand_text = "KcartBot"
            bbox = draw.textbbox((0, 0), brand_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, height - 25), brand_text, fill=(100, 100, 100), font=font)
            
        except Exception as e:
            logger.warning(f"Could not add dashboard text: {e}")
    
    def _create_basic_image(self, product_name: str) -> Dict[str, Any]:
        """Create a basic image as last resort."""
        try:
            from PIL import Image, ImageDraw
            import io
            
            image = Image.new('RGB', (400, 300), color=(240, 248, 255))
            draw = ImageDraw.Draw(image)
            
            draw.ellipse([150, 100, 250, 200], fill=(39, 174, 96))
            draw.text((170, 220), product_name[:15], fill=(0, 0, 0))
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            image_data = base64.b64encode(img_byte_arr).decode('utf-8')
            
            return {
                "success": True,
                "image_data": image_data,
                "image_url": None,
                "api_used": "basic_fallback",
                "prompt": f"Basic image: {product_name}",
                "timestamp": datetime.now().isoformat(),
                "image_id": str(uuid.uuid4()),
                "is_placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Basic image creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_image_data_url(self, image_data: str) -> str:
        """Convert base64 image data to data URL for HTML display."""
        return f"data:image/png;base64,{image_data}"

# Global instance
image_generator = DashboardImageGenerator()