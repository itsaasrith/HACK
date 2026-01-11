import streamlit as st
import os
from database.shop_db import init_shop_db, add_item, get_all_items

init_shop_db()

UPLOAD_DIR = "uploads/shop_items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("🛒 DAMMED Community Shop")

tab1, tab2 = st.tabs(["📤 Sell Item", "🛍️ Buy Items"])

# ---------------- SELL ITEM ----------------
with tab1:
    st.subheader("Upload Item for Sale")

    seller = st.text_input("Seller Name")
    item_name = st.text_input("Item Name")
    description = st.text_area("Item Description")
    price = st.number_input("Price (₹)", min_value=0.0)
    image = st.file_uploader("Upload Item Image", type=["jpg", "png", "jpeg"])

    if st.button("Upload Item"):
        if image and item_name and seller:
            image_path = os.path.join(UPLOAD_DIR, image.name)
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())

            add_item(seller, item_name, description, price, image_path)
            st.success("✅ Item uploaded successfully!")
        else:
            st.error("❌ Please fill all required fields")

# ---------------- BUY ITEMS ----------------
with tab2:
    st.subheader("Available Items")

    items = get_all_items()

    if not items:
        st.info("No items available yet.")
    else:
        for item in items:
            _, seller, name, desc, price, img = item

            st.image(img, width=200)
            st.markdown(f"""
            **{name}**  
            Seller: {seller}  
            Price: ₹{price}  
            {desc}
            """)
            st.button(f"Buy {name}")
            st.divider()
