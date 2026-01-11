import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re


# ================= SAFE JSON PARSER =================
def safe_json_loads(text):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except:
        return None

# ================= CONFIG =================
genai.configure(api_key="AIzaSyD2Tp1eB1MUmokyIgRE2hP0vf6lLkL6Lo4")

vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="Circular Economy AI", layout="centered")

st.title("♻️ Circular Economy Multi-Agent AI")
st.caption("Swachh Bharat • Sustainability • Open Innovation")

# ================= AGENT 1: MULTI-ITEM DETECTION =================
def detection_agent(image):
    prompt = """
    Analyze the image carefully.

    Detect ALL distinct usable or discardable items.
    Ignore background objects.

    Respond ONLY with VALID JSON.
    Do NOT include markdown or explanations.

    STRICT FORMAT:
    {
      "items": [
        {
          "item_name": "string",
          "primary_material": "string",
          "condition": "new | used | damaged",
          "quantity": number
        }
      ]
    }
    """
    response = vision_model.generate_content([prompt, image])
    return response.text.strip()

# ================= AGENT 2: SORTING =================
def sorting_agent(item):
    prompt = f"""
    You are a circular economy sorting agent.

    Item:
    {item}

    Return ONLY JSON with:
    - category
    - sustainability_type (recyclable / reusable / upcyclable / e-waste / biodegradable)
    - estimated_weight_kg
    - carbon_category (low / medium / high)
    """
    response = text_model.generate_content(prompt)
    return response.text.strip()

# ================= AGENT 3: USAGE + CO₂ =================
def usage_agent(sorted_item):
    prompt = f"""
    You are a sustainability and carbon-impact decision agent.

    Input:
    {sorted_item}

    Return ONLY JSON with:
    - best_sustainable_action
    - two_reuse_or_upcycle_ideas
    - estimated_resale_value_in_inr
    - potential_buyers
    - estimated_co2_emission_if_disposed_kg
    - estimated_co2_saved_by_sustainable_action_kg
    - sustainability_score_out_of_100

    Use realistic approximate values.
    """
    response = text_model.generate_content(prompt)
    return response.text.strip()

# ================= GOVERNMENT CREDIT LOGIC =================
def calculate_green_credits(co2_saved):
    # 1 kg CO₂ saved = 10 credits
    credits = int(co2_saved * 10)
    cash_reward = credits * 2  # ₹2 per credit (mock)
    return credits, cash_reward

# ================= SESSION STATE =================
if "results" not in st.session_state:
    st.session_state.results = None

# ================= UI =================
uploaded_file = st.file_uploader(
    "📸 Upload an image with multiple used/waste items",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🚀 Analyze Sustainably"):
        with st.spinner("Running autonomous agents..."):

            detection_text = detection_agent(image)
            detection_data = safe_json_loads(detection_text)

            if not detection_data or "items" not in detection_data:
                st.error("❌ Detection failed. Please try a clearer image.")
                st.stop()

            all_items = detection_data["items"]

            # ===== SELECT ONLY TOP 2 ITEMS (QUOTA SAFE) =====
            MAX_ITEMS = 2
            selected_items = sorted(
                all_items,
                key=lambda x: x.get("quantity", 1),
                reverse=True
            )[:MAX_ITEMS]

            remaining_items = all_items[MAX_ITEMS:]

            results = []

            for item in selected_items:
                sorting = sorting_agent(item)
                usage = usage_agent(sorting)

                results.append({
                    "item": item,
                    "sorting": sorting,
                    "usage": usage
                })

            st.session_state.results = {
                "processed": results,
                "skipped": remaining_items
            }

# ================= RESULTS =================
if st.session_state.results:

    total_credits = 0
    total_cash = 0

    # ===== PROCESSED ITEMS =====
    for idx, result in enumerate(st.session_state.results["processed"]):
        st.subheader(f"📦 Processed Item {idx + 1}")

        st.json(result["item"])
        st.code(result["sorting"], language="json")
        st.code(result["usage"], language="json")

        try:
            usage_data = json.loads(result["usage"])
            co2_saved = float(
                usage_data.get("estimated_co2_saved_by_sustainable_action_kg", 0)
            )
            credits, cash = calculate_green_credits(co2_saved)
            total_credits += credits
            total_cash += cash
        except:
            pass

    # ===== SKIPPED ITEMS =====
    if st.session_state.results["skipped"]:
        st.subheader("📦 Other Detected Items (Skipped for Cost Optimization)")
        for item in st.session_state.results["skipped"]:
            st.json({
                "item_name": item["item_name"],
                "quantity": item["quantity"],
                "note": "Detected but not deeply analyzed to optimize API usage"
            })

    # ===== GOVERNMENT REWARDS =====
    st.subheader("🏛️ Government Sustainability Rewards")
    st.success(f"""
    🌱 Total Green Credits Earned: **{total_credits}**
    💰 Estimated Cash Incentive: **₹{total_cash}**
    """)
    st.caption("✔ Logged to Government Sustainability Cloud (Simulated)")

    # ===== MARKETPLACE =====
    st.subheader("💰 Marketplace Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("🛒 Sell Item")

    with col2:
        st.button("🤝 Donate")

    with col3:
        st.button("♻️ Recycle Nearby")
