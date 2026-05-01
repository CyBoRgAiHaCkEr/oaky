import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

# 1. Setup
st.set_page_config(page_title="Marina Enclave Move AI", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing! Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# 2. The 413 Fix (Force-Shrink Images)
def process_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail((800, 800)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# 3. UI Layout
st.title("📦 Family Move: L-1304 ➡️ I-2103")
st.sidebar.info("Tenants: Viaan, Nosh, & Delnaz")

tab1, tab2 = st.tabs(["💬 Moving Help", "🎨 Design Help"])

# --- TAB 1: JUST TELL GROQ WE NEED HELP ---
with tab1:
    st.header("Logistics Assistant")
    user_msg = st.text_input("Ask anything about the move:", placeholder="e.g. How do we start the move?")
    
    if st.button("Ask Groq"):
        with st.spinner("Talking to Groq..."):
            # System prompt tells Groq the family context automatically
            response = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {"role": "system", "content": "The family (Viaan, Nosh, and Delnaz) is moving from Wing L-1304 to I-2103 in Marina Enclave, Mumbai. They need general help and guidance with the move. Be supportive and practical."},
                    {"role": "user", "content": user_msg if user_msg else "We are moving today, help us out with a plan."}
                ]
            )
            st.markdown(response.choices[0].message.content)

# --- TAB 2: INTERIOR DESIGN (Fixed for 413) ---
with tab2:
    st.header("Interior Designer")
    room_photo = st.file_uploader("Upload a photo of the new house", type=['jpg', 'jpeg', 'png'])

    if room_photo:
        st.image(room_photo, caption="Wing I View", width=400)
        
        if st.button("Analyze Room Layout"):
            with st.spinner("Analyzing..."):
                try:
                    optimized_b64 = process_image(room_photo)
                    vision_res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "This is the new house for Viaan, Nosh, and Delnaz. Suggest a modern furniture layout for them."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{optimized_b64}"}}
                            ]
                        }]
                    )
                    st.write(vision_res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {e}")
