import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# Set page title
st.title("Sheet Metal Label Generator")

# Font handling
try:
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        st.warning("Helvetica not found at /System/Library/Fonts/Helvetica.ttc, falling back to DejaVu Sans.")
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("No suitable font found.")
    large_font = ImageFont.truetype(font_path, 160)  # Color title, increased to 160pt
    medium_font = ImageFont.truetype(font_path, 100)  # Material/gauge and status, 100pt
    st.success(f"Fonts loaded successfully from {font_path}: 160pt and 100pt.")
except Exception as e:
    st.error(f"Font loading error: {e}")
    large_font = ImageFont.load_default()
    medium_font = ImageFont.load_default()
    st.warning("Using default font; sizes may be smaller than expected.")

# Color mappings
color_map = {
    "Snowdrift White": (239, 240, 241), "Bone White": (225, 225, 212),
    "Regal White": (227, 231, 230), "Stone White": (223, 225, 222),
    "Medium Bronze": (89, 79, 68), "Almond": (211, 203, 183),
    "Sandstone": (196, 194, 177), "Sierra Tan": (163, 143, 124),
    "Dark Bronze": (58, 54, 53), "Aged Copper": (138, 169, 142),
    "Dove Gray": (143, 147, 145), "Ash Gray": (163, 159, 149),
    "Slate Gray": (118, 117, 111), "Charcoal Gray": (83, 86, 88),
    "Patina Green": (123, 133, 112), "Evergreen": (55, 82, 69),
    "Slate Blue": (84, 118, 132), "Regal Blue": (38, 80, 105),
    "Banner Red": (159, 36, 50), "Colonial Red": (111, 52, 46),
    "Terra Cotta": (154, 74, 57), "Mansard Brown": (72, 56, 51),
    "Matte Black": (48, 49, 47), "Mill Finish": (204, 204, 204),
    "Bright Silver": "gradient", "Pre-Weathered": "gradient",
    "Copper Penny": "gradient"
}

gradient_map = {
    "Bright Silver": [(189, 193, 196), (240, 240, 240), (189, 193, 196)],
    "Pre-Weathered": [(129, 133, 136), (99, 99, 99), (129, 133, 136)],
    "Copper Penny": [(172, 113, 71), (215, 125, 19), (172, 113, 71)]
}

# Input widgets
color_options = list(color_map.keys()) + ["Other"]
color = st.selectbox("Color:", color_options)

custom_color = None
custom_color_rgb = None
mill_finish_image = None
if color == "Other":
    custom_color = st.text_input("Enter custom color name:", "")
    custom_color_hex = st.color_picker("Pick a color:", "#000000")
    custom_color_rgb = tuple(int(custom_color_hex[i:i+2], 16) for i in (1, 3, 5))
elif color == "Mill Finish":
    mill_finish_image = st.file_uploader("Upload Mill Finish Image", type=["png", "jpg", "jpeg"])

material_options = ["Aluminum", "Steel", "Copper", "Galvalume", "Other"]
material = st.selectbox("Material:", material_options)
if material == "Other":
    material = st.text_input("Enter custom material:", "")

gauge_options = ["24ga", ".032", "22ga", "Other"]
gauge = st.selectbox("Gauge:", gauge_options)
if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["Open", "Reserved"])
project = ""
if status == "Reserved":
    project = st.text_input("Project Name:", "")

# Generate label function
def draw_gradient(draw, x, y, width, height, colors):
    start, middle, end = colors
    for i in range(height):
        if i < height // 2:
            r = int(start[0] + (middle[0] - start[0]) * (i / (height / 2)))
            g = int(start[1] + (middle[1] - start[1]) * (i / (height / 2)))
            b = int(start[2] + (middle[2] - start[2]) * (i / (height / 2)))
        else:
            r = int(middle[0] + (end[0] - middle[0]) * ((i - height / 2) / (height / 2)))
            g = int(middle[1] + (end[1] - middle[1]) * ((i - height / 2) / (height / 2)))
            b = int(middle[2] + (end[2] - middle[2]) * ((i - height / 2) / (height / 2)))
        draw.line([(x, y + i), (x + width, y + i)], fill=(r, g, b))

# Generate and display label
if st.button("Generate Label"):
    width, height = 1650, 586  # Increased height by 16px (8px original + 8px additional) for top margin
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Color block, shifted down 16px
    if color == "Other" and custom_color_rgb:
        draw.rectangle([0, 16, 449, 566], fill=custom_color_rgb)
        color_text = custom_color or "Unknown"
    elif color == "Mill Finish" and mill_finish_image:
        img = Image.open(mill_finish_image).resize((449, 550))
        image.paste(img, (0, 16))
        color_text = "Mill Finish"
    else:
        color_text = color
        if color in color_map:
            if color_map[color] == "gradient":
                draw_gradient(draw, 0, 16, 449, 550, gradient_map[color])
            else:
                draw.rectangle([0, 16, 449, 566], fill=color_map[color])
    draw.rectangle([0, 16, 449, 566], outline="black", width=5)

    # Text area with simulated bold
    material_text = f"{gauge} {material}".strip()
    status_text = project if status == "Reserved" and project else status
    status_color = (95, 178, 34) if status == "Open" else (0, 99, 150)

    # Color title (160pt, bolder), moved down 20px + 16px margin
    x, y = 459, 36  # y=0 + 20 (shift) + 16 (margin) = 36
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), color_text, font=large_font, fill="black")
    draw.line([(459, 336), (1650, 336)], fill="black", width=5)  # Divider, shifted down 16px
    # Material/gauge (100pt) above status, shifted down 16px
    x, y = 459, 346  # y=330 + 16 = 346
    for offset_x in [-1, 0, 1]:
        for offset_y in [-1, 0, 1]:
            draw.text((x + offset_x, y + offset_y), material_text, font=medium_font, fill="black")
    # Status block, shifted down 16px
    status_y = 456  # y=440 + 16 = 456
    draw.rectangle([459, status_y, 1650, status_y + 105], fill=status_color)
    draw.text((459, status_y + 5), status_text, font=medium_font, fill="white")

    # Display the image with centered styling
    with st.container():
        st.image(image, caption="Generated Label", use_container_width=True)

    # Download button
    img_buffer = image.save("label.png", "PNG", quality=100)
    with open("label.png", "rb") as file:
        st.download_button(
            label="Download Label",
            data=file,
            file_name="label.png",
            mime="image/png"
        )

# Note about saving on Streamlit Cloud
st.info("Note: The 'Download Label' button allows you to save the label locally. Streamlit Cloud doesn't persist saved files.")
