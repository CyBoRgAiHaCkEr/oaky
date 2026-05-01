import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Marina Enclave AI", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing! Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 2. THE 413 FIX (IMAGE OPTIMIZER) ---
def process_for_groq(uploaded_file):
    # Open the image
    img = Image.open(uploaded_file)
    # Convert to RGB (removes alpha channel which bulks up size)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Force resize to a max of 800px (AI doesn't need more to see the room)
    img.thumbnail((800, 800)) 
    
    # Save with aggressive compression
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# --- 3. UI ---
st.title("🏢 Marina Enclave: L-1304 ➡️ I-2103")
st.sidebar.write("### Tenants: Viaan, Nosh, Delnaz")

tab1, tab2 = st.tabs(["🚚 Shifting Logistics", "🎨 Interior Design"])

# --- TAB 1: LOGISTICS (GROQ/COMPOUND) ---
with tab1:
    st.header("Move Planner")
    move_input = st.text_area("What are we moving?", placeholder="e.g. 3 beds, fridge, 20 boxes...", key="logistic_text")
    
    if st.button("Get Move Strategy"):
        if move_input:
            with st.spinner("Calculating..."):
                res = client.chat.completions.create(
                    model="groq/compound",
                    messages=[{"role": "user", "content": f"Plan a move from L-1304 to I-2103 in Marina Enclave for Viaan, Nosh, and Delnaz. Items: {move_input}"}]
                )
                st.markdown(res.choices[0].message.content)
        else:
            st.warning("Input items first!")

# --- TAB 2: INTERIOR DESIGN (VISION + GENERATION) ---
with tab2:
    st.header("Home Designer")
    room_photo = st.file_uploader("Upload Room Photo", type=['jpg', 'jpeg', 'png'])

    if room_photo:
        st.image(room_photo, caption="Current View", width=400)
        
        if st.button("Analyze & Generate Design"):
            with st.spinner("Optimizing & Analyzing..."):
                try:
                    # Apply the fix
                    optimized_b64 = process_for_groq(room_photo)
                    
                    # Vision Call
                    vision_res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this room and suggest a modern layout for Viaan, Nosh, and Delnaz. Be specific about furniture placement."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{optimized_b64}"}}
                            ]
                        }]
                    )
                    
                    analysis = vision_res.choices[0].message.content
                    st.subheader("AI Design Analysis")
                    st.write(analysis)
                    
                    # Generate Prompt for Image Generation
                    st.divider()
                    st.subheader("🖼️ Use this prompt in DALL-E/Midjourney:")
                    st.code(f"Photorealistic interior design for a Mumbai high-rise apartment, 21st floor, modern style, based on: {analysis[:200]}", language="text")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
