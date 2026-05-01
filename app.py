import streamlit as st
from groq import Groq
import requests # To call image generation APIs

# --- INITIALIZATION ---
st.set_page_config(page_title="Marina Enclave Design AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["🚚 Logistics Planner", "🎨 Interior Designer"])

# --- TAB 1: LOGISTICS (Your previous code goes here) ---
with tab1:
    st.header("Move: L-1304 ➡️ I-2103")
    # ... (Insert previous logistics code)

# --- TAB 2: INTERIOR DESIGNER ---
with tab2:
    st.header("Design your new home in Wing I")
    
    col_up, col_gen = st.columns(2)
    
    with col_up:
        st.subheader("Upload Room Photo")
        uploaded_file = st.file_uploader("Upload a photo of your living room or bedroom in I-2103", type=['jpg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, caption="Current Layout", use_container_width=True)

    with col_gen:
        st.subheader("Generate Design Ideas")
        style = st.selectbox("Select Theme", ["Modern Minimalist", "Bohemian", "Mumbai Contemporary", "Luxury Gold"])
        requirements = st.text_input("Special requests?", "e.g., L-shaped sofa, work-from-home desk near window")
        
        if st.button("Generate Design Visual"):
            with st.spinner("Groq is architecting your room..."):
                # 1. Use Groq to create a professional image prompt
                design_prompt_query = f"Create a detailed DALL-E prompt for a {style} interior design of a Mumbai apartment room with {requirements}. Focus on lighting and space."
                
                completion = client.chat.completions.create(
                    model="groq/compound",
                    messages=[{"role": "user", "content": design_prompt_query}]
                )
                refined_prompt = completion.choices[0].message.content
                
                # 2. Call an Image Gen API (Example: OpenAI DALL-E)
                # You would need an OPENAI_API_KEY in your secrets for this part
                try:
                    # This is a placeholder for the image generation call
                    # response = openai_client.images.generate(prompt=refined_prompt, n=1, size="1024x1024")
                    # image_url = response.data[0].url
                    # st.image(image_url, caption=f"AI Generated {style} Concept")
                    st.info("Visual generation requires connecting an Image API (like DALL-E or Replicate).")
                    st.write("**Groq's Design Suggestion:**")
                    st.write(refined_prompt)
                except Exception as e:
                    st.error(f"Image Error: {e}")

st.sidebar.markdown("### 🏠 Move Members\n- Viaan\n- Nosh\n- Delnaz")
