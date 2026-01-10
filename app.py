import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------- CONFIG ----------------
genai.configure(api_key=["GEMINI_API_KEY"])


vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="Circular Economy AI", layout="centered")

st.title("♻️ Circular Economy Multi-Agent AI")
st.caption("Swachh Bharat • Sustainability • Open Innovation")

---------------- AGENT 1: DETECTION ----------------
def detection_agent(image):
    prompt = """
    Detect the main item in the image.

    Identify:
    - Item name
    - Primary material
    - Condition (new / used / damaged)

    Respond ONLY in JSON.
    """
    response = vision_model.generate_content([prompt, image])
    return response.text

---------------- AGENT 2: SORTING ----------------
def sorting_agent(detection_output):
    prompt = f"""
    You are a circular economy sorting agent.

    Based on this detection:
    {detection_output}

    Classify the item and return ONLY JSON with:
    - category
    - sustainability_type (recyclable / reusable / upcyclable / e-waste / biodegradable)
    - estimated_weight_kg
    - carbon_category (low / medium / high)
    """
    response = text_model.generate_content(prompt)
    return response.text

# ---------------- AGENT 3: USAGE + CO2 ----------------
def usage_agent(classification_output):
    prompt = f"""
    You are a sustainability and carbon-impact decision agent.

    Based on this input:
    {classification_output}

    Suggest and return ONLY JSON with:
    - best_sustainable_action
    - 2 reuse_or_upcycle_ideas
    - estimated_resale_value_in_inr
    - potential_buyers
    - estimated_co2_emission_if_disposed_kg
    - estimated_co2_saved_by_sustainable_action_kg
    - sustainability_score_out_of_100

    Use realistic but approximate values.
    """
    response = text_model.generate_content(prompt)
    return response.text

# ---------------- SESSION STATE ----------------
if "result" not in st.session_state:
    st.session_state.result = None

# ---------------- UI ----------------
uploaded_file = st.file_uploader(
    "📸 Upload an image of waste or used product",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🚀 Analyze Sustainably"):
        with st.spinner("Running multi-agent AI..."):
            detection = detection_agent(image)
            sorting = sorting_agent(detection)
            usage = usage_agent(sorting)

            st.session_state.result = {
                "detection": detection,
                "sorting": sorting,
                "usage": usage
            }

# ---------------- RESULTS ----------------
if st.session_state.result:
    st.subheader("🕵️ Detection Agent")
    st.code(st.session_state.result["detection"], language="json")

    st.subheader("🧮 Sorting Agent")
    st.code(st.session_state.result["sorting"], language="json")

    st.subheader("♻️ Usage, Value & CO₂ Impact Agent")
    st.code(st.session_state.result["usage"], language="json")

    st.success("✅ Analysis Complete")

    # ---------------- MARKETPLACE ----------------
    st.subheader("💰 Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("Sell Item")

    with col2:
        st.button("Donate")

    with col3:
        st.button("Recycle Nearby")



