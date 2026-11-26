import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
import tempfile
import os
import shutil
from datetime import datetime

st.set_page_config(page_title="AI Video Studio Pro", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Generator Studio Pro")
st.write("Apni pasand ke **Style** aur **Ratio** mein bilkul FREE AI videos banayein!")

if "video_library" not in st.session_state:
    st.session_state.video_library = []

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Video Settings")
    
    ratio_choice = st.selectbox(
        "📐 Video Ratio Chunein:",
        [
            "16:9 (YouTube / Landscape)",
            "9:16 (TikTok / Reels / Shorts)",
            "1:1 (Instagram Square)",
            "4:3 (Classic TV)"
        ]
    )
    
    style_choice = st.selectbox(
        "🎨 Video Style Chunein:",
        [
            "3D Cartoon (Pixar / Disney Style)",
            "Realistic / Cinematic",
            "Anime / Japanese Animation",
            "2D Classic Cartoon",
            "Claymation / Toy Style"
        ]
    )
    
    st.markdown("---")
    st.info(f"📚 Library mein mehfooz videos: **{len(st.session_state.video_library)}**")

style_prompts = {
    "Realistic / Cinematic": "photorealistic, ultra detailed, 4k cinematic lighting, real life",
    "3D Cartoon (Pixar / Disney Style)": "3D animated movie style, Pixar and Disney animation, cute vibrant colors, smooth 3D render",
    "Anime / Japanese Animation": "high quality anime style, Studio Ghibli inspired, vibrant 2D Japanese animation",
    "2D Classic Cartoon": "colorful 2D cartoon animation, expressive hand-drawn cartoon style",
    "Claymation / Toy Style": "stop motion claymation style, cute miniature clay world, soft studio lighting"
}

ratio_dimensions = {
    "16:9 (YouTube / Landscape)": (768, 448),
    "9:16 (TikTok / Reels / Shorts)": (448, 768),
    "1:1 (Instagram Square)": (512, 512),
    "4:3 (Classic TV)": (640, 480)
}

selected_style_text = style_prompts[style_choice]
width, height = ratio_dimensions[ratio_choice]

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
        value="A cute little baby panda eating bamboo in a magical glowing forest, happy smile, cinematic lighting"
    )
    
    if st.button("Text se Video Banayein 🎥", key="btn_text"):
        if not text_prompt:
            st.warning("⚠️ Meharbani karke pehle prompt likhein.")
        else:
            full_prompt = f"{text_prompt}, {selected_style_text}"
            with st.spinner(f"{style_choice} mein video ban rahi hai... (1 se 2 minute intezar karein)"):
                try:
                    # Free Public LTX-Video Server
                    client = Client("Lightricks/ltx-video-distilled")
                    result = client.predict(
                        prompt=full_prompt,
                        negative_prompt="worst quality, blurry, jittery, distorted",
                        input_image_filepath=None,
                        input_video_filepath=None,
                        height_ui=height,
                        width_ui=width,
                        mode="text-to-video",
                        duration_ui=2.0,
                        ui_frames_to_use=9,
                        seed_ui=42,
                        randomize_seed=True,
                        ui_guidance_scale=3.0,
                        improve_texture_flag=True,
                        api_name="/text_to_video"
                    )
                    
                    video_path = result[0]["video"] if isinstance(result[0], dict) else result[0]
                    with open(video_path, "rb") as f:
                        video_bytes = f.read()
                    
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
                    st.error(f"Free server abhi busy hai, 1 minute baad dubara click karein. Details: {e}")

# --- TAB 2: IMAGE TO VIDEO ---
with tab2:
    st.subheader("Apni tasveer upload karein aur us mein harkat dalein")
    st.caption(f"Selected: **{style_choice}** | **{ratio_choice}**")
    
    uploaded_file = st.file_uploader("Tasveer chunein (JPG ya PNG):", type=["jpg", "jpeg", "png"])
    img_prompt = st.text_input(
        "Tasveer mein kya harkat honi chahiye? (English mein):",
        value="Smiling happily, gentle wind blowing hair, smooth camera zoom"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Upload ki gayi tasveer", width=300)
        
    if st.button("Image se Video Banayein 🎞️", key="btn_img"):
        if uploaded_file is None:
            st.warning("⚠️ Pehle koi tasveer upload karein.")
        else:
            full_img_prompt = f"{img_prompt}, {selected_style_text}"
            with st.spinner("Tasveer ko video mein badla ja raha hai... (1-2 minute intezar karein)"):
                try:
                    # Tasveer ko temporary file mein save karna
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        image.convert("RGB").resize((width, height)).save(tmp.name)
                        temp_img_path = tmp.name
                    
                    client = Client("Lightricks/ltx-video-distilled")
                    result = client.predict(
                        prompt=full_img_prompt,
                        negative_prompt="worst quality, blurry, jittery, distorted",
                        input_image_filepath=handle_file(temp_img_path),
                        input_video_filepath=None,
                        height_ui=height,
                        width_ui=width,
                        mode="image-to-video",
                        duration_ui=2.0,
                        ui_frames_to_use=9,
                        seed_ui=42,
                        randomize_seed=True,
                        ui_guidance_scale=3.0,
                        improve_texture_flag=True,
                        api_name="/image_to_video"
                    )
                    
                    video_path = result[0]["video"] if isinstance(result[0], dict) else result[0]
                    with open(video_path, "rb") as f:
                        video_bytes = f.read()
                        
                    os.remove(temp_img_path)
                    
                    st.session_state.video_library.insert(0, {
                        "title": img_prompt[:40] + "...",
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
                    st.error(f"Free server abhi busy hai, 1 minute baad dubara click karein. Details: {e}")

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
