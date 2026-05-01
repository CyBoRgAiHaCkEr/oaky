import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

st.set_page_config(page_title="Marina Enclave AI", layout="wide")

# API Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY to Secrets!")
    st.stop()

# --- HELPER: Optimize Image to avoid 413 Error ---
def process_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Resize to max 1024px width/height to keep file size small
    img.thumbnail((1024, 1024)) 
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85) # Compress to 85% quality
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- SIDEBAR ---
st.sidebar.title("🏢 Team: Viaan, Nosh, Delnaz")
mode = st.sidebar.selectbox("Choose Mode", ["Moving Chatbot", "Room Designer"])

# --- MODE 1: MOVING CHATBOT ---
if mode == "Moving Chatbot":
    st.header("💬 Logistics Chat: L-1304 to I-2103")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ayy! Ready to move to the 21st floor. What's the plan for today?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about the move..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Using groq/compound for reasoning
            response = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {"role": "system", "content": "You are a logistics expert helping Viaan, Nosh, and Delnaz move from Wing L-1304 to I-2103 in Marina Enclave, Mumbai. Be helpful and witty."},
                    *st.session_state.messages
                ]
            )
            full_res = response.choices[0].message.content
            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

# --- MODE 2: ROOM DESIGNER ---
else:
    st.header("🎨 Design Vision")
    up_file = st.file_uploader("Upload Room Photo", type=['jpg','png'])
    
    if up_file:
        st.image(up_file, caption="New Space in Wing I", width=400)
        
        if st.button("Analyze & Design"):
            with st.spinner("Shrinking image & analyzing..."):
                try:
                    base64_img = process_image(up_file) # The Fix for Error 413
                    
                    res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this room and suggest a modern layout for 3 roommates."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                            ]
                        }]
                    )
                    st.success("Design Analysis:")
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Still hitting a limit: {e}")
