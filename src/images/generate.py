from PIL import Image, ImageDraw, ImageFont
from typing import Optional


def generate_product_image(product_name: str, out_path: str, price: Optional[float] = None) -> str:
	img = Image.new("RGB", (800, 600), color=(240, 255, 240))
	draw = ImageDraw.Draw(img)
	text = product_name if price is None else f"{product_name} - {price} ETB/kg"
	try:
		font = ImageFont.truetype("arial.ttf", 40)
	except Exception:
		font = ImageFont.load_default()
	draw.text((50, 250), text, fill=(0, 100, 0), font=font)
	img.save(out_path)
	return out_path
