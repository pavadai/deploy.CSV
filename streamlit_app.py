# color_detector_app.py
import streamlit as st
from PIL import Image
import numpy as np
import io
import math
import pandas as pd

st.set_page_config(page_title="Color Detector", layout="centered")

st.title("🎨 Color Detection from Image")
st.write("Upload an image, click to detect a color, and see the color name, RGB values, and color box.")

# --- small color dataset (common named colors) ---
# This is a compact list; feel free to expand or replace with a CSV.
COLOR_LIST = [
    ("Black", (0,0,0)),
    ("White", (255,255,255)),
    ("Red", (255,0,0)),
    ("Lime", (0,255,0)),
    ("Blue", (0,0,255)),
    ("Yellow", (255,255,0)),
    ("Cyan", (0,255,255)),
    ("Magenta", (255,0,255)),
    ("Silver", (192,192,192)),
    ("Gray", (128,128,128)),
    ("Maroon", (128,0,0)),
    ("Olive", (128,128,0)),
    ("Green", (0,128,0)),
    ("Purple", (128,0,128)),
    ("Teal", (0,128,128)),
    ("Navy", (0,0,128)),
    ("Orange", (255,165,0)),
    ("Pink", (255,192,203)),
    ("Brown", (165,42,42)),
    ("Gold", (255,215,0)),
    # add more rows if you want...
]

def nearest_color_name(target_rgb):
    """Return the name and distance of the nearest color in COLOR_LIST to target_rgb (r,g,b)."""
    tr, tg, tb = target_rgb
    best_name = None
    best_dist = float('inf')
    for name, (r,g,b) in COLOR_LIST:
        # Euclidean distance in RGB space
        dist = (tr - r)**2 + (tg - g)**2 + (tb - b)**2
        if dist < best_dist:
            best_dist = dist
            best_name = name
    # Return real euclidean distance's sqrt for interpretability if needed
    return best_name, math.sqrt(best_dist)

# Sidebar: upload
st.sidebar.header("https://sl.bing.net/ggxI9TY9nuC")
uploaded_file = st.sidebar.file_uploader("Choose an image (PNG/JPG)", type=['png','jpg','jpeg'])

# Try to import optional helper for click coordinates
USE_CLICK = False
try:
    # This package provides st.image_coords which lets user click and returns (x,y)
    from streamlit_image_coordinates import streamlit_image_coordinates
    USE_CLICK = True
except Exception:
    USE_CLICK = False

if uploaded_file is None:
    st.info("Upload an image from the left sidebar to begin.")
    st.stop()

# Load image as PIL
image = Image.open(uploaded_file).convert("RGB")
img_width, img_height = image.size

# Display image
st.subheader("Image")
st.caption(f"Image size: {img_width} × {img_height} (W × H)")

if USE_CLICK:
    st.write("Click anywhere on the image below to detect that pixel's color.")
    # streamlit_image_coordinates returns dict like {'x':..., 'y':...} or None
    coords = streamlit_image_coordinates(image, key="coords")
    x = None; y = None
    if coords is not None and 'x' in coords and 'y' in coords and coords['x'] is not None:
        x = int(coords['x'])
        y = int(coords['y'])
else:
    st.write("Clicking on the image is not available (missing `streamlit-image-coordinates`).")
    st.write("Either install it with `pip install streamlit-image-coordinates` or enter coordinates manually below.")
    st.image(image, use_column_width=True)
    coords = None
    # Manual coordinate input
    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("X (0 = left)", min_value=0, max_value=img_width-1, value=img_width//2, step=1)
    with col2:
        y = st.number_input("Y (0 = top)", min_value=0, max_value=img_height-1, value=img_height//2, step=1)

# Button to confirm detect (helps avoid instant re-eval when clicking)
if st.button("Detect color"):
    # Ensure we have integer coordinates
    if x is None or y is None:
        st.error("No coordinates available. Click on the image or enter X and Y.")
    else:
        # Extract pixel RGB
        px = image.getpixel((int(x), int(y)))  # (r,g,b)
        r, g, b = px
        st.subheader("Detected color")
        st.write(f"Position: **X = {int(x)}**, **Y = {int(y)}** (origin: top-left)")
        st.write(f"RGB: **({r}, {g}, {b})**")

        # Find nearest name
        name, distance = nearest_color_name((r,g,b))
        st.write(f"Nearest name: **{name}** (RGB distance ≈ {distance:.1f})")

        # Show color box and hex
        hex_code = '#{:02X}{:02X}{:02X}'.format(r,g,b)
        st.markdown(f"**Hex:** `{hex_code}`")

        # display swatch
        swatch_html = f"""
        <div style="
            width:140px;
            height:80px;
            border-radius:8px;
            border:1px solid #ddd;
            background: linear-gradient(90deg, {hex_code}, {hex_code});
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
        "></div>
        """
        st.markdown(swatch_html, unsafe_allow_html=True)

        # Show a small table of RGB components
        df = pd.DataFrame({
            "Component": ["R", "G", "B"],
            "Value": [r, g, b]
        })
        st.table(df)

        # Optional: give a small palette of closest named colors (top 5)
        dists = []
        for nm, (cr, cg, cb) in COLOR_LIST:
            dist = math.sqrt((r-cr)**2 + (g-cg)**2 + (b-cb)**2)
            dists.append((dist, nm, (cr,cg,cb)))
        dists.sort()
        st.subheader("Closest named colors (top 5)")
        cols = st.columns(5)
        for i, (dist, nm, (cr,cg,cb)) in enumerate(dists[:5]):
            with cols[i]:
                h = '#{:02X}{:02X}{:02X}'.format(cr, cg, cb)
                st.markdown(f"**{nm}**")
                st.markdown(f"`{h}`")
                box = f"""<div style="width:60px;height:40px;border-radius:6px;border:1px solid #ddd;background:{h}"></div>"""
                st.markdown(box, unsafe_allow_html=True)

# Helpful note about installation if click feature not available
if not USE_CLICK:
    st.warning(
        "To enable clicking on the image, install the optional package: "
        "`pip install streamlit-image-coordinates` and then re-run this app. "
        "Otherwise, pick X and Y manually."
    )

st.caption("Tip: X increases to the right; Y increases downwards (0,0 is the top-left).")
