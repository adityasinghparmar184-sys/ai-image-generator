import streamlit as st
from google import genai
from PIL import Image
import io

st.set_page_config(page_title="Free AI Image Generator", page_icon="🎨")
st.title("🎨 Free Image Generator (Gemini Powered)")

# Streamlit Secrets se API Key check karna
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add GEMINI_API_KEY to your Streamlit Secrets!")
    st.stop()

# Client initialize karein
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Quick Prompts
st.subheader("💡 Quick Prompts")
col1, col2 = st.columns(2)
with col1:
    p1 = st.button("🐱 Cat astronaut in space")
    p2 = st.button("🏙️ Futuristic city at night")
with col2:
    p3 = st.button("🤖 Cute robot holding flowers")
    p4 = st.button("🏰 Underwater castle")

# Prompt select karne ka logic
prompt = ""
if p1: prompt = "Cat astronaut in space, highly detailed, cinematic"
if p2: prompt = "Futuristic city at night, neon lights, cyberpunk style"
if p3: prompt = "Cute robot holding flowers, pixar style, 3d render"
if p4: prompt = "Underwater castle, mythical, glowing sea life"

user_prompt = st.text_input("Ya phir apna khud ka prompt likhein:", value=prompt)

if st.button("🚀 Generate Image", type="primary"):
    if user_prompt:
        with st.spinner("Gemini aapki image bana raha hai... Kripya intezar karein..."):
            try:
                # Gemini Imagen 3 model se image banana
                response = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=user_prompt,
                    config=dict(number_of_images=1, aspect_ratio="1:1")
                )
                
                # Image ko screen par dikhana
                for generated_image in response.generated_images:
                    image_bytes = generated_image.image.image_bytes
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=user_prompt, use_container_width=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Image",
                        data=image_bytes,
                        file_name="gemini_image.jpg",
                        mime="image/jpeg"
                    )
            except Exception as e:
                st.error(f"❌ Generation Failed: {e}")
    else:
        st.warning("Pehle koi prompt toh likhiye!")
                  
