from PIL import Image, ImageDraw, ImageFont

# Create a new image with a purple background
width, height = 400, 200
background_color = (128, 0, 128)  # Purple color in RGB
image = Image.new('RGB', (width, height), background_color)

# Initialize ImageDraw
draw = ImageDraw.Draw(image)

# Load a font
try:
    font = ImageFont.truetype("arial.ttf", 40)
except IOError:
    font = ImageFont.load_default()

# Text to be written
text = "OCA"
text_color = (255, 255, 255)  # White color for the text

# Calculate text size and position
text_width, text_height = draw.textsize(text, font=font)
text_position = ((width - text_width) // 2, (height - text_height) // 2)

# Draw the text on the image
draw.text(text_position, text, fill=text_color, font=font)

# Save the image
image.save('icon.png')
