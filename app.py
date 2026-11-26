import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
import tempfile
import os
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips

st.set_page_config(page_title="AI Disney & Video Studio Pro", page_icon="👑", layout="centered")

st.title("👑 AI Disney & Video Studio Pro")
st.write("Pixar/Disney jaisi khoobsurat **3D Cartoon** aur **10s se 60s** tak ki videos banayein!")

if "video_library" not in st.session_state:
    st.session_state.video_library = []

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Studio Settings")
    
    duration_choice = st.selectbox(
        "⏱️ Video Length (Duration):",
        [
            "5 Seconds (Fast Preview - 1 Clip)",
            "10 Seconds (2 Scenes Merged)",
            "15 Seconds (3 Scenes Merged)",
            "30 Seconds (6 Scenes Merged)",
            "60 Seconds (12 Scenes - Full Story)"
        ],
        index=1
    )
    
    ratio_choice = st.selectbox(
        "📐 Video Ratio:",
        [
            "9:16 (TikTok / Reels / Shorts)",
            "16:9 (YouTube / Landscape)",
            "1:1 (Instagram Square)",
            "4:3 (Classic TV)"
        ]
    )
    
    style_choice = st.selectbox(
        "🎨 Video Style Chunein:",
        [
            "👑 Disney / Pixar 3D Princess (Ultra Cute)",
            "✨ Magical Fairy Tale 3D Animation",
            "🌸 Studio Ghibli / High-End Anime",
            "🎥 Ultra Realistic 4K Cinematic",
            "🧸 Cute Claymation / Toy World"
        ]
    )
    
    st.markdown("---")
    st.info(f"📚 Library mein mehfooz videos: **{len(st.session_state.video_library)}**")

clips_map = {
    "5 Seconds (Fast Preview - 1 Clip)": 1,
    "10 Seconds (2 Scenes Merged)": 2,
    "15 Seconds (3 Scenes Merged)": 3,
    "30 Seconds (6 Scenes Merged)": 6,
    "60 Seconds (12 Scenes - Full Story)": 12
}
num_clips = clips_map[duration_choice]
seconds_label = duration_choice.split(" ")[0]

scene_variations = [
    "wide establishing shot, magical atmosphere",
    "close up portrait shot, expressive big eyes, smiling",
    "medium shot, gentle movement, sparkling lights around",
    "cinematic camera pan, glowing fairy dust, vibrant colors",
    "over the shoulder shot, dreamy fantasy background",
    "dynamic camera angle, soft golden hour glow"
]

style_prompts = {
    "👑 Disney / Pixar 3D Princess (Ultra Cute)": (
        "masterpiece 3D Disney Pixar animation style, ultra cute character design, "
        "large expressive glossy eyes, soft skin texture, intricate dress details, "
        "magical glowing fairy tale lighting, Unreal Engine 5 render, 8k resolution, vibrant colors"
    ),
    "✨ Magical Fairy Tale 3D Animation": (
        "enchanted 3D fantasy movie style, DreamWorks and Disney 3D render, "
        "sparkling magic particles, dreamy pastel colors, ultra high detail, smooth animation"
    ),
    "🌸 Studio Ghibli / High-End Anime": (
        "gorgeous Makoto Shinkai and Studio Ghibli anime style, shimmering light, "
        "highly detailed expressive face, lush magical scenery, 4k anime movie quality"
    ),
    "🎥 Ultra Realistic 4K Cinematic": (
        "photorealistic 8k cinema camera, dramatic golden lighting, shallow depth of field, "
        "hyper-detailed textures, natural smooth motion"
    ),
    "🧸 Cute Claymation / Toy World": (
        "adorable 3D stop-motion claymation style, soft studio lighting, "
        "handcrafted miniature world, vibrant cheerful colors, Pixar short film look"
    )
}

ratio_dimensions = {
    "9:16 (TikTok / Reels / Shorts)": (480, 832),
    "16:9 (YouTube / Landscape)": (832, 480),
    "1:1 (Instagram Square)": (640, 640),
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
    st.subheader("Apni Kahani ya Scene Likhein")
    st.caption(f"Length: **{duration_choice}** | Style: **{style_choice}** | Ratio: **{ratio_choice}**")
    
    text_prompt = st.text_area(
        "Video Prompt (English mein likhein):",
        value="A beautiful little princess with golden braided hair and big sparkling blue eyes holding a glowing magic wand inside an enchanted crystal castle, cute smile"
    )
    
    if st.button("High-Quality Video Banayein ✨", key="btn_text"):
        if not text_prompt:
            st.warning("⚠️ Meharbani karke pehle prompt likhein.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            temp_files = []
            
            try:
                client = Client("Lightricks/ltx-video-distilled")
                
                for i in range(num_clips):
                    status_text.info(f"🎬 Scene {i + 1} of {num_clips} ban raha hai... (Har scene mein ~40 sec lagte hain)")
                    variation = scene_variations[i % len(scene_variations)]
                    full_prompt = f"{text_prompt}, {variation}, {selected_style_text}"
                    
                    result = client.predict(
                        prompt=full_prompt,
                        negative_prompt="worst quality, low quality, ugly, deformed face, blurry, pixelated, jittery, distorted hands, extra limbs, watermark, text",
                        input_image_filepath=None,
                        input_video_filepath=None,
                        height_ui=height,
                        width_ui=width,
                        mode="text-to-video",
                        duration_ui=5.0,
                        ui_frames_to_use=25,
                        seed_ui=42 + i,
                        randomize_seed=True,
                        ui_guidance_scale=4.5,
                        improve_texture_flag=True,
                        api_name="/text_to_video"
                    )
                    
                    clip_path = result["video"] if isinstance(result, dict) else result
                    temp_files.append(clip_path)
                    progress_bar.progress((i + 1) / num_clips)
                
                status_text.info("🎞️ Saare scenes ko jor kar final HD MP4 video tayyar ki ja rahi hai...")
                
                if len(temp_files) == 1:
                    final_video_path = temp_files[0]
                else:
                    clips = [VideoFileClip(p) for p in temp_files]
                    final_clip = concatenate_videoclips(clips, method="compose")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as out_tmp:
                        final_video_path = out_tmp.name
                    final_clip.write_videofile(final_video_path, codec="libx264", audio=False, logger=None)
                    for c in clips:
                        c.close()
                
                with open(final_video_path, "rb") as f:
                    video_bytes = f.read()
                
                st.session_state.video_library.insert(0, {
                    "title": text_prompt[:40] + "...",
                    "type": f"Text ({seconds_label}s)",
                    "style": style_choice,
                    "ratio": ratio_choice,
                    "time": datetime.now().strftime("%I:%M %p"),
                    "video": video_bytes
                })
                
                status_text.empty()
                st.success(f"🎉 Mubarak ho! Aapki {seconds_label} second ki HD Cartoon Video tayyar hai!")
                st.video(video_bytes)
                st.download_button(
                    label="⬇️ Download HD MP4 Video",
                    data=video_bytes,
                    file_name=f"disney_ai_video_{datetime.now().strftime('%H%M%S')}.mp4",
                    mime="video/mp4",
                    key="dl_text_now"
                )
            except Exception as e:
                st.error(f"Free server abhi busy hai, thori der baad dubara koshish karein. Details: {e}")

# --- TAB 2: IMAGE TO VIDEO ---
with tab2:
    st.subheader("Apni Tasveer ko Zinda (Animate) Karein")
    st.caption(f"Length: **{duration_choice}** | Style: **{style_choice}** | Ratio: **{ratio_choice}**")
    
    uploaded_file = st.file_uploader("Tasveer chunein (JPG ya PNG):", type=["jpg", "jpeg", "png"])
    img_prompt = st.text_input(
        "Tasveer mein kya harkat honi chahiye? (English mein):",
        value="Cute princess blinking big sparkling eyes, gentle smile, hair blowing softly in magic wind, glowing sparkles"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Upload ki gayi tasveer", width=280)
        
    if st.button("Image se HD Video Banayein 🎞️", key="btn_img"):
        if uploaded_file is None:
            st.warning("⚠️ Pehle koi tasveer upload karein.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            temp_files = []
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.convert("RGB").resize((width, height)).save(tmp.name)
                    temp_img_path = tmp.name
                
                client = Client("Lightricks/ltx-video-distilled")
                
                for i in range(num_clips):
                    status_text.info(f"🎬 Part {i + 1} of {num_clips} animate ho raha hai...")
                    variation = scene_variations[i % len(scene_variations)]
                    full_img_prompt = f"{img_prompt}, {variation}, {selected_style_text}"
                    
                    result = client.predict(
                        prompt=full_img_prompt,)
