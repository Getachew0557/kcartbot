#!/usr/bin/env python3
"""
Demo script for REALISTIC image generation functionality
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.image_generation import image_generator

def demo_realistic_image_generation():
    """Demonstrate REALISTIC image generation for Ethiopian agricultural products."""
    
    print("🖼️  KcartBot REALISTIC Image Generation Demo")
    print("=" * 60)
    print("Generating photorealistic Ethiopian agricultural product images")
    print()
    
    # Comprehensive test products
    test_products = [
        {"name": "Tomato", "description": "Fresh red Ethiopian tomatoes"},
        {"name": "Red Onion", "description": "Ethiopian red onions with purple skin"}, 
        {"name": "Avocado", "description": "Creamy Ethiopian avocados"},
        {"name": "Potato", "description": "Fresh Ethiopian potatoes"},
        {"name": "Banana", "description": "Sweet Ethiopian bananas"},
        {"name": "Milk", "description": "Fresh Ethiopian milk"},
        {"name": "Cabbage", "description": "Green Ethiopian cabbage"},
        {"name": "Carrot", "description": "Orange Ethiopian carrots"},
        {"name": "Ethiopian Coffee", "description": "Fresh coffee beans"},
        {"name": "Ayib", "description": "Traditional Ethiopian cheese"},
        {"name": "Mango", "description": "Sweet Ethiopian mangoes"},
        {"name": "Papaya", "description": "Fresh Ethiopian papaya"}
    ]
    
    successful_generations = 0
    api_usage = {}
    
    print(f"📦 Generating REALISTIC images for {len(test_products)} Ethiopian products...")
    print()
    
    for product in test_products:
        print(f"🎨 Generating REALISTIC image for: {product['name']}")
        print(f"   Description: {product['description']}")
        
        try:
            # Generate realistic image
            result = image_generator.generate_product_image(
                product_name=product['name'],
                product_description=product['description'],
                style="photorealistic"
            )
            
            if result["success"]:
                successful_generations += 1
                api_used = result["api_used"]
                api_usage[api_used] = api_usage.get(api_used, 0) + 1
                
                print(f"   ✅ REALISTIC image generated successfully!")
                print(f"   API Used: {api_used}")
                
                # Save image to file
                filename = f"realistic_{product['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%H%M%S')}.png"
                saved_path = image_generator.save_image_to_file(
                    result['image_data'], 
                    filename
                )
                print(f"   💾 Saved to: {saved_path}")
                
                if result.get('is_placeholder'):
                    print("   ⚠️  Using realistic fallback (enable AI APIs for photorealistic)")
                else:
                    print("   🎯 AI-generated realistic image ready!")
                
            else:
                print(f"   ❌ Image generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 REALISTIC IMAGE GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"   Total Ethiopian products: {len(test_products)}")
    print(f"   Successful generations: {successful_generations}")
    print(f"   Success rate: {(successful_generations/len(test_products))*100:.1f}%")
    print(f"\n   Image Quality Sources:")
    for api, count in api_usage.items():
        quality = "🟢 AI Photorealistic" if "huggingface" in api else "🟡 Real Photos" if "unsplash" in api else "🟠 Realistic Placeholder"
        print(f"     • {quality}: {count} images")
    
    print(f"\n🎉 Realistic image generation demo completed!")
    print(f"📁 Generated images saved to: data/generated_images/")
    
    if 'realistic_fallback' in api_usage or 'fallback' in api_usage:
        print(f"\n💡 For BETTER QUALITY images:")
        print(f"   1. Get FREE Hugging Face token: https://huggingface.co/settings/tokens")
        print(f"   2. Update .env file with your token")
        print(f"   3. Run demo again for AI-generated photorealistic images!")
    else:
        print(f"\n✅ Excellent! All images generated using AI APIs!")

if __name__ == "__main__":
    demo_realistic_image_generation()