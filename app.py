import streamlit as st
import google.generativeai as genai
from PIL import Image
import json, re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from auth.auth_manager import register_user, login_user
from storage.db import add_entry, fetch_user_entries, fetch_all_users

# ================= CONFIG =================
st.set_page_config(page_title="Circular Economy AI", page_icon="♻️", layout="centered")

genai.configure(api_key="AIzaSyDn3diBfZtHv7X21adqmBRRnW4xHSAms48")
vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.5-flash")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= UI =================
st.title("♻️ Circular Economy Multi-Agent AI")
st.caption("Swachh Bharat • Sustainability • Government Incentives")

st.markdown("""
<style>
.card {
    padding: 1.2rem;
    border-radius: 12px;
    background-color: #0e1117;
    border: 1px solid #262730;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
def safe_json(text):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except:
        return None

# ================= AGENT A: DETECTION (IMAGE OR TEXT) =================
def agent_a_detection(image=None, text=None):
    prompt = """
    Detect ALL usable or discardable items.

    Return ONLY JSON:
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
    if image:
        return vision_model.generate_content([prompt, image]).text
    else:
        return text_model.generate_content(f"{prompt}\nText:\n{text}").text

# ================= AGENT B: SUSTAINABILITY DECISION =================
def agent_b_decision(item):
    prompt = f"""
    Item:
    {item}

    Perform ALL of the following:
    - Categorize item
    - Decide sustainability type
    - Choose best sustainable action
    - Estimate resale value
    - Estimate CO₂ saved
    - Give sustainability score

    Return ONLY JSON:
    {{
      "category": "string",
      "sustainability_type": "recyclable | reusable | upcyclable | e-waste | biodegradable",
      "best_sustainable_action": "reuse | upcycle | recycle | resell | donate",
      "estimated_resale_value_in_inr": number,
      "estimated_co2_saved_kg": number,
      "sustainability_score_out_of_100": number
    }}
    """
    return text_model.generate_content(prompt).text

# ================= AGENT C: GOVERNMENT + DIY =================
def agent_c_government_diy(item, decision):
    prompt = f"""
    Item:
    {item}

    Sustainability decision:
    {decision}

    Government policy:
    1 kg CO₂ saved = 10 Green Points

    Suggest DIY or practical actions based on preferred action.

    Return ONLY JSON:
    {{
      "government_green_points": number,
      "recommended_action_type": "DIY | household | community",
      "step_by_step_actions": ["step 1", "step 2", "step 3"],
      "tools_required": ["tool1", "tool2"],
      "estimated_time_minutes": number
    }}
    """
    return text_model.generate_content(prompt).text

# ================= CERTIFICATE =================
def generate_certificate(username, points, co2):
    filename = f"{username}_certificate.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(w/2, h-150, "Government Sustainability Certificate")

    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h-230, "This certifies that")

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-270, username)

    c.drawCentredString(w/2, h-330, f"has reduced {round(co2,2)} kg of CO₂ emissions")
    c.drawCentredString(w/2, h-370, f"and earned {points} Green Points")

    c.drawCentredString(
        w/2, h-440,
        f"Issued on {datetime.now().strftime('%d %B %Y')}"
    )

    c.showPage()
    c.save()
    return filename

# ================= AUTH =================
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(u, p):
                st.success("Registered! Login now.")
            else:
                st.error("User already exists")

    st.stop()

# ================= MAIN =================
st.success(f"Welcome, {st.session_state.user}")

tab_input, tab_results, tab_dashboard, tab_leaderboard = st.tabs(
    ["📥 Input", "📊 Results", "🌱 Dashboard", "🏆 Leaderboard"]
)

# ================= INPUT =================
with tab_input:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    mode = st.radio("Input type", ["Upload Image", "Enter Text"], horizontal=True)

    uploaded_file, text_input = None, None
    if mode == "Upload Image":
        uploaded_file = st.file_uploader("Upload image", ["jpg","png","jpeg"])
    else:
        text_input = st.text_area("Describe items", height=120)

    analyze = st.button("🚀 Run 3-Agent Analysis")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= PIPELINE =================
results = []

if analyze and (uploaded_file or text_input):
    with st.spinner("Running optimized agents..."):

        detected = safe_json(
            agent_a_detection(
                image=Image.open(uploaded_file) if uploaded_file else None,
                text=text_input
            )
        )

        for item in detected["items"][:2]:
            decision = safe_json(agent_b_decision(item))
            gov_diy = safe_json(agent_c_government_diy(item, decision))

            entry = {
                "item": item,
                "decision": decision,
                "government_diy": gov_diy,
                "co2_saved_kg": decision["estimated_co2_saved_kg"],
                "government_points": gov_diy["government_green_points"],
                "time": datetime.now().isoformat()
            }

            add_entry(st.session_state.user, entry)
            results.append(entry)

# ================= RESULTS =================
with tab_results:
    if results:
        for r in results:
            st.json(r)
            st.success(
                f"🌍 CO₂ Saved: {r['co2_saved_kg']} kg | 🏛️ Points: {r['government_points']}"
            )
    else:
        st.info("No analysis yet.")

# ================= DASHBOARD =================
with tab_dashboard:
    entries = fetch_user_entries(st.session_state.user)
    total_co2 = sum(e["co2_saved_kg"] for e in entries)
    total_points = sum(e["government_points"] for e in entries)

    st.metric("🌍 Total CO₂ Reduced (kg)", round(total_co2,2))
    st.metric("🏛️ Government Green Points", total_points)

    if st.button("📄 Download Certificate"):
        pdf = generate_certificate(st.session_state.user, total_points, total_co2)
        with open(pdf, "rb") as f:
            st.download_button("Download Certificate", f, file_name=pdf)

# ================= LEADERBOARD =================
with tab_leaderboard:
    leaderboard = []
    for u in fetch_all_users():
        e = fetch_user_entries(u)
        leaderboard.append({
            "User": u,
            "CO₂ Saved (kg)": round(sum(x["co2_saved_kg"] for x in e),2),
            "Green Points": sum(x["government_points"] for x in e)
        })

    leaderboard = sorted(leaderboard, key=lambda x: x["Green Points"], reverse=True)
    st.table(leaderboard)
