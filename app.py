import streamlit as st  
import openai  
import os  
import requests  
import json  
import time  
from PIL import Image  
from io import BytesIO  
from dotenv import load_dotenv  
  
# ─── Setup ───  
load_dotenv()  

# API Key check karne ke liye secure logic
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ OpenAI API Key nahi mili! Kripya Streamlit Advanced Settings (Secrets) me ya .env file me 'OPENAI_API_KEY' set karein.")
    st.stop()

client = openai.OpenAI(api_key=api_key)  
HISTORY_FILE = "history.json"  
  
st.set_page_config(page_title="🎨 AI Image Generator Pro", page_icon="🖼️", layout="wide")  
  
# ─── Persistent History ───  
def load_history():  
    if os.path.exists(HISTORY_FILE):  
        try:  
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:  
                return json.load(f)  
        except:  
            return []  
    return []  
  
def save_history(history):  
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:  
        json.dump(history, f, indent=2, ensure_ascii=False)  
  
if "history" not in st.session_state:  
    st.session_state.history = load_history()  
  
# ─── Custom CSS ───  
st.markdown("""  
<style>  
    .title { font-size:38px !important; font-weight:bold; text-align:center; margin-bottom:10px; }  
    .img-card { background:#f9f9f9; padding:15px; border-radius:12px; border:1px solid #eee; }  
    .img-card img { border-radius:10px; width:100%; box-shadow:0 4px 12px rgba(0,0,0,0.15); }  
    .cost-badge { background:#e3f2fd; padding:4px 10px; border-radius:20px; font-size:12px; display:inline-block; }  
    .progress-bar { height:8px !important; border-radius:4px !important; }  
</style>  
""", unsafe_allow_html=True)  
  
# ─── Header ───  
st.markdown('<p class="title">🎨 AI Image Generator Pro</p>', unsafe_allow_html=True)  
st.write("✨ Powered by DALL·E 3 • Persistent History • Smart Enhancer • Thumbnail Mode")  
  
# ─── Sidebar ───  
with st.sidebar:  
    st.header("⚙️ Settings")  
      
    style = st.selectbox("🎨 Art Style", [  
        "Natural", "Photorealistic", "Cartoon", "Anime",   
        "Oil Painting", "Watercolor", "Pixel Art", "Cyberpunk",  
        "Fantasy", "Minimalist", "Surreal", "3D Render",  
        "YouTube Thumbnail", "Wallpaper", "Logo Design"  
    ])  
      
    quality = st.selectbox("✨ Quality", ["standard", "hd"])  
    size = st.selectbox("📐 Size", ["1024x1024", "1792x1024 (Landscape)", "1024x1792 (Portrait)"])  
    size_map = {  
        "1024x1024": "1024x1024",  
        "1792x1024 (Landscape)": "1792x1024",  
        "1024x1792 (Portrait)": "1024x1792"  
    }  
      
    st.divider()  
    st.markdown("🚫 **Avoid (Negative Prompt)**")  
    avoid_text = st.text_input("e.g., blurry, ugly, low quality", placeholder="Auto-converted to positive constraints")  
      
    st.markdown("🧠 **Smart Enhancer**")  
    use_enhancer = st.toggle("Auto-add professional keywords", value=True)  
      
    st.divider()  
    st.markdown("💰 **Cost:**")  
    st.caption("Standard: $0.04/image")  
    st.caption("HD: $0.08/image")  
      
    if st.button("🗑️ Clear History", use_container_width=True):  
        st.session_state.history = []  
        save_history([])  
        st.rerun()  
  
# ─── Helper Functions ───  
def build_prompt(user_prompt, style, avoid_text, use_enhancer):  
    base = user_prompt.strip()  
    if use_enhancer:  
        base += ", highly detailed, professional composition, cinematic lighting, sharp focus, masterpiece"  
    if avoid_text.strip():  
        base += f", clean rendering, avoid {avoid_text.lower()}"  
    base += f", {style.lower()} style"  
    return base  
  
def simulate_progress():  
    progress = st.progress(0, text="🔍 Analyzing prompt...")  
    steps = [  
        (0.25, "🎨 Generating composition..."),  
        (0.50, "✨ Rendering details & textures..."),  
        (0.75, "🖌️ Applying style & lighting..."),  
        (1.00, "✅ Finalizing image...")  
    ]  
    for pct, msg in steps:  
        time.sleep(0.6)  
        progress.progress(pct, text=msg)  
    progress.empty()  
  
# ─── Tabs ───  
tab1, tab2, tab3, tab4 = st.tabs(["🎨 Create", "📺 AI Thumbnail", "💡 Examples", "📜 History"])  
  
# TAB 1: Generate  
with tab1:  
    col1, col2 = st.columns([2, 1])  
    with col1:  
        # Session state to handle prompt switching from examples dynamically
        if "prompt_input" not in st.session_state:
            st.session_state.prompt_input = ""
        prompt = st.text_area("Describe your image:", height=120, value=st.session_state.prompt_input,  
                              placeholder="A majestic dragon sitting on a mountain at sunset, dramatic lighting...")  
    with col2:  
        st.markdown("### 💡 Quick Prompts")  
        quick = ["Cat astronaut in space", "Futuristic city at night", "Cute robot holding flowers",   
                 "Underwater castle", "Samurai in cherry blossoms"]  
        for q in quick:  
            if st.button(q, key=f"quick_{q}", use_container_width=True):  
                st.session_state.prompt_input = q  
                st.rerun()  
  
    if prompt and len(prompt) > 4000:  
        st.error("⚠️ Prompt too long! DALL·E 3 max is 4000 characters.")  
        prompt = None  
  
    btn_col1, btn_col2 = st.columns(2)  
    with btn_col1:  
        generate = st.button("🚀 Generate Image", type="primary", use_container_width=True, disabled=not prompt)  
    with btn_col2:  
        variation = st.button("🔄 New Variation", use_container_width=True, disabled=not prompt)  
  
    if generate or variation:  
        enhanced = build_prompt(prompt, style, avoid_text, use_enhancer)  
          
        with st.status("🎨 AI is creating your image...", expanded=True) as status:  
            simulate_progress()  
            try:  
                response = client.images.generate(  
                    model="dall-e-3", prompt=enhanced,   
                    size=size_map[size], quality=quality, n=1  
                )  
                image_url = response.data[0].url  
                revised = response.data[0].revised_prompt  
                  
                status.update(label="✅ Generation Complete!", state="complete")  
                  
                st.markdown("---")  
                st.markdown(f"### 🖼️ Your Creation")  
                st.caption(f"💡 AI refined prompt: `{revised}`")  
                  
                img_resp = requests.get(image_url)  
                img = Image.open(BytesIO(img_resp.content))  
                  
                col_img, col_act = st.columns([3, 1])  
                with col_img:  
                    st.markdown('<div class="img-card">', unsafe_allow_html=True)  
                    st.image(img, use_container_width=True)  
                    st.markdown('</div>', unsafe_allow_html=True)  
                  
                with col_act:  
                    st.markdown("### 📥 Actions")  
                    buf = BytesIO()  
                    img.save(buf, format="PNG")  
                    st.download_button("💾 Download PNG", buf.getvalue(), "ai_image.png", "image/png", use_container_width=True)  
                      
                    if st.button("🔗 Copy URL", use_container_width=True):  
                        st.code(image_url)  
                      
                    cost = 0.08 if quality == "hd" else 0.04  
                    st.markdown(f'<span class="cost-badge">💰 ${cost:.2f}</span>', unsafe_allow_html=True)  
                      
                    entry = {"prompt": prompt, "url": image_url, "style": style, "revised": revised}  
                    st.session_state.history.append(entry)  
                    save_history(st.session_state.history)  
                    st.success("✅ Saved to permanent history!")  
                      
            except Exception as e:  
                status.update(label="❌ Generation Failed", state="error")  
                st.error(f"Error: {str(e)}")  
                st.info("💡 Tips: Keep prompts <4000 chars, avoid copyrighted names, check API key.")  
  
# TAB 2: AI Thumbnail Generator  
with tab2:  
    st.header("📺 YouTube Thumbnail Generator")  
    st.info("Optimized for 16:9. Uses `1792x1024` (crop-friendly for 1280x720).")  
      
    thumb_prompt = st.text_area("Thumbnail Concept:", height=100,   
                                placeholder="Shocked face pointing at glowing text, neon background, high contrast...")  
    thumb_style = st.selectbox("Thumbnail Vibe", ["Gaming", "Tech Review", "Vlog", "Finance", "Reaction", "Tutorial"])  
      
    if st.button("🎬 Generate Thumbnail", type="primary", disabled=not thumb_prompt):  
        full_prompt = f"YouTube thumbnail: {thumb_prompt}, {thumb_style} style, bold text space, high contrast, eye-catching, {style.lower()} style"  
        with st.spinner("🎬 Designing thumbnail..."):  
            try:  
                res = client.images.generate(model="dall-e-3", prompt=full_prompt, size="1792x1024", quality="hd", n=1)  
                st.image(res.data[0].url, caption="📺 Thumbnail Preview (Crop to 1280x720)")  
                st.success("✅ Ready for upload! Add text in Canva/Photoshop.")  
            except Exception as e:  
                st.error(f"❌ {e}")  
  
# TAB 3: Examples  
with tab3:  
    st.header("💡 Prompt Ideas & Templates")  
    examples = [  
        ("🐱 Cat Astronaut", "Fluffy orange cat in space suit, Earth background, photorealistic, cinematic lighting"),  
        ("🏙️ Cyberpunk City", "Neon rainy street, holograms, flying cars, Blade Runner style, ultra detailed"),  
        ("🐉 Dragon", "Golden dragon coiled around castle, fantasy oil painting, dramatic clouds"),  
        ("📈 Finance Thumbnail", "Money raining down, shocked businessman, bold 'MILLIONAIRE' text space, high contrast"),  
        ("🎮 Gaming Thumbnail", "Epic sword clash, glowing particles, dark background, dynamic pose, 3D render"),  
        ("🤖 AI Robot", "Friendly robot watering flowers, warm sunset, cartoon style, soft shadows")  
    ]  
    cols = st.columns(2)  
    for i, (title, p) in enumerate(examples):  
        with cols[i % 2]:  
            st.markdown(f"**{title}**")  
            st.code(p)  
            if st.button("📋 Use", key=f"ex_{i}"):  
                st.session_state.prompt_input = p  
                st.rerun()  
  
# TAB 4: Persistent History  
with tab4:  
    st.header("📜 Generation History (Auto-Saved)")  
    if st.session_state.history:  
        for i, item in enumerate(reversed(st.session_state.history)):  
            with st.expander(f"🖼️ {item['prompt'][:60]}... | {item['style']}"):  
                st.image(item["url"], width=500)  
                st.caption(item.get("revised", item["prompt"]))  
                buf = BytesIO()  
                try:  
                    resp = requests.get(item["url"])  
                    img = Image.open(BytesIO(resp.content))  
                    img.save(buf, format="PNG")  
                    st.download_button("💾 Download", buf.getvalue(), f"gen_{i}.png", "image/png", key=f"dl_{i}")  
                except:  
                    st.warning("⚠️ Image expired or unavailable")  
    else:  
        st.info("🎨 No images yet. Generate your first one!")  
  
# ─── Footer ───  
st.divider()  
c1, c2, c3, c4 = st.columns(4)  
c1.caption("🤖 DALL·E 3")  
c2.caption("💾 JSON History")  
c3.caption("🧠 Smart Enhancer")  
c4.caption("📺 Thumbnail Mode") 
