import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

# 1. Setup & API Initialization
st.set_page_config(page_title="Marina Enclave Move AI", layout="wide")

# Ensure GROQ_API_KEY is in your Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key missing! Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# Helper function for Vision
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# 2. Sidebar Navigation
st.sidebar.title("🏠 Marina Enclave Hub")
st.sidebar.write("**Tenants:** Viaan, Nosh, Delnaz")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Choose Service", ["Logistics Planner", "Interior Designer"])

# ---------------------------------------------------------
# MODE 1: LOGISTICS PLANNER
# ---------------------------------------------------------
if app_mode == "Logistics Planner":
    st.header("🚚 Move Logistics: L-1304 ➡️ I-2103")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # FIXED: Added keys to ensure text input works perfectly
        move_items = st.text_area(
            "List your furniture and boxes:", 
            placeholder="e.g. 2 Queen beds, 1 Fridge, 15 carton boxes...",
            key="items_input"
        )
        move_date = st.date_input("Shifting Date", key="date_input")

    with col2:
        st.info("📍 **Route Note:** Internal move between Wing L and Wing I. Requires podium or basement transit.")
        lift_booking = st.checkbox("Have you booked the Service Lift in Wing I?", key="lift_check")
        noc_status = st.checkbox("Owner NOCs received?", key="noc_check")

    if st.button("Generate Detailed Move Plan"):
        if not move_items:
            st.error("Please enter your items first so the AI can calculate labor!")
        else:
            with st.spinner("Groq/Compound is analyzing the route..."):
                prompt = f"""
                Users: Viaan, Nosh, and Delnaz.
                Task: Shifting within Marina Enclave, Malad West.
                Route: Wing L-1304 (13th Floor) to Wing I-2103 (21st Floor).
                Items: {move_items}.
                
                Provide a professional logistics breakdown:
                1. Recommended path (Podium vs Basement).
                2. Estimated labor crew size.
                3. Timeline for a 3-person tenant move.
                4. Specific Mumbai society formalities for Marina Enclave.
                """
                
                response = client.chat.completions.create(
                    model="groq/compound",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("Logistics Strategy Ready:")
                st.markdown(response.choices[0].message.content)

# ---------------------------------------------------------
# MODE 2: INTERIOR DESIGNER
# ---------------------------------------------------------
else:
    st.header("🎨 Interior Design & Vision")
    st.write("Upload a photo of your new space in I-2103.")

    uploaded_room = st.file_uploader("Upload Room Photo", type=['jpg', 'jpeg', 'png'], key="room_upload")

    if uploaded_room:
        st.image(uploaded_room, caption="Wing I-2103 Current View", width=600)
        
        design_style = st.selectbox("Select Design Style", ["Modern Minimalist", "Mumbai Luxury", "Boho-Chic"], key="style_select")

        if st.button("Analyze & Generate Design Prompt"):
            base64_img = encode_image(uploaded_room)
            
            with st.spinner("Analyzing layout..."):
                # Vision analysis
                vision_res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Analyze this room. Suggest a {design_style} layout for 3 tenants (Viaan, Nosh, Delnaz)."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                
                analysis = vision_res.choices[0].message.content
                st.subheader("Architectural Suggestions")
                st.write(analysis)
                
                st.divider()
                st.subheader("🖼️ Image Generation Prompt")
                st.info("Copy the text below into an image generator like DALL-E or Midjourney:")
                st.code(f"High-quality interior design render of a Mumbai apartment, {design_style} style, floor 21, based on these specs: {analysis[:300]}", language="text")

st.sidebar.markdown("---")
st.sidebar.caption("Marina Enclave Move Assistant v2.0")
