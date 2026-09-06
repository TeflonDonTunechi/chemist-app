from PIL import Image, ImageDraw, ImageFont

# Create a simple icon
size = 256
img = Image.new('RGB', (size, size), color='#6c3b9e')
draw = ImageDraw.Draw(img)

# Draw a pill shape
draw.ellipse([40, 80, 216, 176], fill='white', outline='white', width=3)
draw.ellipse([40, 80, 216, 176], fill='#4a6a8a', outline='white', width=3)

# Draw cross
draw.line([128, 60, 128, 196], fill='white', width=8)
draw.line([68, 128, 188, 128], fill='white', width=8)

# Save
img.save('icon.png')
print("Icon created: icon.png")
