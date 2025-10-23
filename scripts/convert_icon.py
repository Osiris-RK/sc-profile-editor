"""
Quick script to convert logo.png to icon.ico with high quality
"""
from PIL import Image

# Open the PNG file
img = Image.open('../assets/logo.png')

# Convert to RGBA if not already
img = img.convert('RGBA')

# Get original size
original_size = img.size
print(f"Original image size: {original_size}")

# If the image is smaller than 256x256, we should upscale it first for better quality
max_size = max(original_size)
if max_size < 256:
    # Upscale using high-quality Lanczos resampling
    scale_factor = 256 / max_size
    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    print(f"Upscaled to: {new_size}")

# Create high-quality versions for each icon size
icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Save as ICO with multiple sizes using best quality resampling
img.save('assets/icon.ico', format='ICO', sizes=icon_sizes)

print(f"Successfully created assets/icon.ico with {len(icon_sizes)} sizes")
print("Icon sizes included:", icon_sizes)
