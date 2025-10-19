# scripts/test_image_format.py
import os
from PIL import Image
import sys

sys.path.append('.')
from src.image_generation import image_generator

def test_image_format():
    """Test that generated images are proper PNG files."""
    print("🧪 Testing Image Format Compatibility")
    print("=" * 50)
    
    test_products = ["Tomato", "Banana", "Carrot"]
    
    for product in test_products:
        print(f"\nTesting: {product}")
        
        # Generate image
        result = image_generator.generate_product_image(product)
        
        if result["success"]:
            # Save image
            filename = f"test_{product.lower()}.png"
            filepath = image_generator.save_image_to_file(result['image_data'], filename)
            
            # Verify the image
            try:
                with Image.open(filepath) as img:
                    print(f"✅ Format: {img.format}")
                    print(f"✅ Size: {img.size}")
                    print(f"✅ Mode: {img.mode}")
                    print(f"✅ File: {filepath}")
                    
                    # Try to load and verify it's readable
                    img.verify()
                    print("✅ Image verified and readable")
                    
            except Exception as e:
                print(f"❌ Image verification failed: {e}")
        else:
            print(f"❌ Generation failed: {result.get('error')}")
    
    print(f"\n🎉 Image format test completed!")

if __name__ == "__main__":
    test_image_format()