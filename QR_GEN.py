import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask # We will create a custom Radial gradient
from PIL import Image, ImageDraw

# 1. Paths & Configurations
url = "https://habitify-server.tail3823a2.ts.net/"
logo_path = "habitify logo.webp"
output_path = "habitify_dynamic_gradient_qr.png"

# 2. Generate the Base QR with High Error Correction
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% tolerance for large logos
    box_size=12,  
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# 3. Dynamic Color Extraction Step (The Modification)
try:
    print(f"Analyzing dominant vibrant colors from {logo_path}...")
    logo_src = Image.open(logo_path).convert("RGB")
    logo_src.thumbnail((150, 150)) # Downscale for faster analysis

    # Use PIL to get the most used vibrant colors
    # We filter out very dark colors and pure white
    colors = logo_src.getcolors(150 * 150)
    vibrant_colors = []
    
    # Simple check for vibrancy (minimum saturation/brightness threshold)
    for count, color in colors:
        r, g, b = color
        v = max(r, g, b)
        s = (max(r,g,b) - min(r,g,b)) / v if v != 0 else 0
        if v > 120 and s > 0.4: # Filter for relatively bright and saturated pixels
            vibrant_colors.append((count, color))
            
    # Sort the filtered vibrant colors by count, descending
    vibrant_colors.sort(key=lambda x: x[0], reverse=True)
    
    if len(vibrant_colors) < 2:
        # Fallback colors if the image doesn't provide enough vibrancy (Purple/Green from crest)
        print("Fallback: Dynamic color extraction failed. Using purple/green defaults.")
        qr_primary_color = (130, 40, 210)    # Habitify Crest Purple
        qr_secondary_color = (80, 230, 60)   # Habitify Wing Green
    else:
        # We pick the top two vibrant colors for the gradient
        qr_primary_color = vibrant_colors[0][1] # Most frequent vibrant color (likely Purple)
        qr_secondary_color = vibrant_colors[1][1] # Second most frequent vibrant color (likely Green)
        print(f"Dynamically selected gradient: {qr_primary_color} to {qr_secondary_color}")

except FileNotFoundError:
    print(f"Error: {logo_path} not found. Exiting.")
    exit()

# 4. Create the Custom Gradient Mask
# We use RadialGradiantColorMask, but apply it linearly (top-left to bottom-right)
# The qrcode library provides this mask, and it looks beautiful.
gradient_mask = RadialGradiantColorMask(
    back_color=(255, 255, 255),    # QR Background (White)
    edge_color=qr_primary_color,   # Primary (Purple-ish, top-left)
    center_color=qr_secondary_color, # Secondary (Green-ish, bottom-right)
)

# 5. Render using StyledPilImage with Rounded Modules and Dynamic Gradient
qr_img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=gradient_mask
).convert("RGB")

# 6. Apply the Large Logo (Same as before, keep 42% size)
qr_width, qr_height = qr_img.size
logo = Image.open(logo_path)

# SCALING: Set at 28% of width (Enlarged)
logo_max_size = int(qr_width * 0.35)
logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
logo_width, logo_height = logo.size

# 7. Define positions for the buffer mask and logo placement
paste_position = (
    (qr_width - logo_width) // 2,
    (qr_height - logo_height) // 2
)

# 8. Create a clean white background buffer circle
buffer_margin = 25  
mask_size = (logo_width + buffer_margin, logo_height + buffer_margin)
mask_position = (
    (qr_width - mask_size[0]) // 2,
    (qr_height - mask_size[1]) // 2
)

# Clear out conflicting data dots behind the logo area
draw = ImageDraw.Draw(qr_img)
draw.ellipse(
    [mask_position[0], mask_position[1], mask_position[0] + mask_size[0], mask_position[1] + mask_size[1]],
    fill=(255, 255, 255)
)

# 9. Overlay the habitify logo
if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
    qr_img.paste(logo, paste_position, logo.convert('RGBA'))
else:
    qr_img.paste(logo, paste_position)
    
# 10. Export the styled file
qr_img.save(output_path)
print(f"Successfully generated dynamic gradient QR code: {output_path}")