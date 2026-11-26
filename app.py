import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io
import os
from datetime import datetime

# Page ki settings
st.set_page_config(page_title="AI Video Studio Pro", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Generator Studio Pro")
st.write("Apni pasand ke **Style** aur **Ratio** mein FREE AI videos banayein!")

# Secrets se API key uthana
API_KEY = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")

# Video Library ko session mein mehfooz rakhna
if "video_library" not in st.session_state:
    st.session_state.video_library = []

# --- SIDEBAR SETTINGS (Ratio & Style) ---
with st.sidebar:
    st.header("⚙️ Video Settings")
    
    # 1. Aspect Ratio (4 Options)
    ratio_choice = st.selectbox(
        "📐 Video Ratio Chunein:",
        [
            "16:9 (YouTube / Landscape)",
            "9:16 (TikTok / Reels / Shorts)",
            "1:1 (Instagram Square)",
            "4:3 (Classic TV)"
        ]
    )
    
    # 2. Style Selector (Cartoon aur doosre styles)
    style_choice = st.selectbox(
        "🎨 Video Style Chunein:",
        [
            "Realistic / Cinematic",
            "3D Cartoon (Pixar / Disney Style)",
            "Anime / Japanese Animation",
            "2D Classic Cartoon",
            "Claymation / Toy Style"
        ]
    )
    
    st.markdown("---")
    st.info(f"📚 Library mein mehfooz videos: **{len(st.session_state.video_library)}**")

# Style aur Ratio ke mutabiq prompt aur dimensions set karna
style_prompts = {
    "Realistic / Cinematic": "photorealistic, ultra detailed, 4k cinematic lighting, real life",
    "3D Cartoon (Pixar / Disney Style)": "3D animated movie style, Pixar and Disney animation, cute vibrant colors, smooth 3D render",
    "Anime / Japanese Animation": "high quality anime style, Studio Ghibli inspired, vibrant 2D Japanese animation",
    "2D Classic Cartoon": "colorful 2D cartoon animation, expressive hand-drawn cartoon style",
    "Claymation / Toy Style": "stop motion claymation style, cute miniature clay world, soft studio lighting"
}

ratio_dimensions = {
    "16:9 (YouTube / Landscape)": (768, 432),
    "9:16 (TikTok / Reels / Shorts)": (432, 768),
    "1:1 (Instagram Square)": (512, 512),
    "4:3 (Classic TV)": (640, 480)
}

selected_style_text = style_prompts[style_choice]
width, height = ratio_dimensions[ratio_choice]

# App ke 3 Tabs: Text-to-Video, Image-to-Video, aur Library
tab1, tab2, tab3 = st.tabs([
    "📝 Text se Video",
    "🖼️ Image se Video",
    f"📚 Meri Video Library ({len(st.session_state.video_library)})"
])

# --- TAB 1: TEXT TO VIDEO ---
with tab1:
    st.subheader("Likhein ke aap kaisi video chahte hain")
    st.caption(f"Selected: **{style_choice}** | **{ratio_choice}**")
    
    text_prompt = st.text_area(
        "Video Prompt (English mein likhein):",
        placeholder="A cute little rabbit jumping in a magical forest..."
    )
    
    if st.button("Text se Video Banayein 🎥", key="btn_text"):
        if not API_KEY:
            st.error("⚠️ API Key missing hai! App settings mein HF_TOKEN add karein.")
        elif not text_prompt:
            st.warning("⚠️ Meharbani karke pehle prompt likhein.")
        else:
            full_prompt = f"{text_prompt}, {selected_style_text}"
            with st.spinner(f"{style_choice} mein video ban rahi hai... (1-2 minute lag sakte hain)"):
                try:
                    client = InferenceClient(provider="hf-inference", api_key=API_KEY)
                    video_bytes = client.text_to_video(
                        full_prompt,
                        model="Lightricks/LTX-Video"
                    )
                    
                    # Library mein save karna
                    st.session_state.video_library.insert(0, {
                        "title": text_prompt[:40] + "...",
                        "type": "Text-to-Video",
                        "style": style_choice,
                        "ratio": ratio_choice,
                        "time": datetime.now().strftime("%I:%M %p"),
                        "video": video_bytes
                    })
                    
                    st.success("🎉 Video tayyar hai aur Library mein save ho gayi hai!")
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ Download MP4",
                        data=video_bytes,
                        file_name=f"ai_video_{datetime.now().strftime('%H%M%S')}.mp4",
                        mime="video/mp4",
                        key="dl_text_now"
                    )
                except Exception as e:
                    st.error(f"Error aaya hai: {e}")

# --- TAB 2: IMAGE TO VIDEO ---
with tab2:
    st.subheader("Apni tasveer upload karein aur us mein harkat dalein")
    st.caption(f"Selected: **{style_choice}** | **{ratio_choice}**")
    
    uploaded_file = st.file_uploader("Tasveer chunein (JPG ya PNG):", type=["jpg", "jpeg", "png"])
    img_prompt = st.text_input(
        "Tasveer mein kya harkat honi chahiye? (English mein):",
        placeholder="Smiling and waving hand, magical sparkles around..."
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Upload ki gayi tasveer", width=300)
        
    if st.button("Image se Video Banayein 🎞️", key="btn_img"):
        if not API_KEY:
            st.error("⚠️ API Key missing hai! App settings mein HF_TOKEN add karein.")
        elif uploaded_file is None:
            st.warning("⚠️ Pehle koi tasveer upload karein.")
        else:
            # Image ko selected ratio ke mutabiq resize karna
            resized_image = image.convert("RGB").resize((width, height))
            img_byte_arr = io.BytesIO()
            resized_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            full_img_prompt = f"{img_prompt if img_prompt else 'smooth motion'}, {selected_style_text}"
            
            with st.spinner("Tasveer ko video mein badla ja raha hai... Thora intezar karein."):
                try:
                    client = InferenceClient(provider="hf-inference", api_key=API_KEY)
                    video_bytes = client.image_to_video(
                        image=img_bytes,
                        prompt=full_img_prompt,
                        model="Wan-AI/Wan2.1-I2V-14B-480P"
                    )
                    
                    # Library mein save karna
                    st.session_state.video_library.insert(0, {
                        "title": img_prompt if img_prompt else "Image Animation",
                        "type": "Image-to-Video",
                        "style": style_choice,
                        "ratio": ratio_choice,
                        "time": datetime.now().strftime("%I:%M %p"),
                        "video": video_bytes
                    })
                    
                    st.success("🎉 Image se video ban gayi hai aur Library mein save ho gayi hai!")
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ Download MP4",
                        data=video_bytes,
                        file_name=f"ai_img_video_{datetime.now().strftime('%H%M%S')}.mp4",
                        mime="video/mp4",
                        key="dl_img_now"
                    )
                except Exception as e:
                    st.error(f"Error aaya hai: {e}")

# --- TAB 3: MERI VIDEO LIBRARY ---
with tab3:
    st.subheader("📚 Aapki Banayi Hui Videos")
    if len(st.session_state.video_library) == 0:
        st.info("Abhi tak koi video nahi banayi gayi. Pehle koi video banayein, woh yahan khud save ho jayegi!")
    else:
        for idx, item in enumerate(st.session_state.video_library):
            with st.container(border=True):
                st.markdown(f"**🎬 {idx + 1}. {item['title']}**")
                st.caption(f"Type: {item['type']} | Style: {item['style']} | Ratio: {item['ratio']} | Time: {item['time']}")
                st.video(item["video"])
                st.download_button(
                    label="⬇️ Download MP4",
                    data=item["video"],
                    file_name=f"library_video_{idx + 1}.mp4",
                    mime="video/mp4",
                    key=f"lib_dl_{idx}"
                )

