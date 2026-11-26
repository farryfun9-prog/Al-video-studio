import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import numpy as np
import tempfile, os
from datetime import datetime
from moviepy.editor import VideoClip, concatenate_videoclips

st.set_page_config(page_title="AI Disney Studio Unlimited", page_icon="👑", layout="centered")
st.title("👑 AI Disney & Cartoon Studio (Unlimited Free)")
st.write("Pixar/Disney 3D Cartoon aur **5s se 60s** tak ki videos banayein — **100% Unlimited & Free!**")

API_KEY = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")

if "video_library" not in st.session_state:
    st.session_state.video_library = []

with st.sidebar:
    st.header("⚙️ Studio Settings")
    dur = st.selectbox("⏱️ Video Length:", ["5 Seconds (1 Scene)", "10 Seconds (2 Scenes)", "15 Seconds (3 Scenes)", "30 Seconds (6 Scenes)", "60 Seconds (12 Scenes)"])
    rat = st.selectbox("📐 Video Ratio:", ["9:16 (TikTok / Reels)", "16:9 (YouTube)", "1:1 (Instagram)", "4:3 (Classic)"])
    sty = st.selectbox("🎨 Cartoon & Video Style:", [
        "👑 Disney / Pixar 3D Princess (Ultra Cute)",
        "✨ Magical Fairy Tale 3D Movie",
        "🌸 Studio Ghibli / High-End Anime",
        "🎥 Ultra Realistic 4K Cinematic",
        "🧸 Cute Claymation / Toy World"
    ])
    st.info(f"📚 Library Videos: **{len(st.session_state.video_library)}**")

clips_map = {"5 Seconds (1 Scene)": 1, "10 Seconds (2 Scenes)": 2, "15 Seconds (3 Scenes)": 3, "30 Seconds (6 Scenes)": 6, "60 Seconds (12 Scenes)": 12}
styles_map = {
    "👑 Disney / Pixar 3D Princess (Ultra Cute)": "masterpiece 3D Disney Pixar animation style, ultra cute character, big sparkling expressive eyes, intricate royal dress, magical fairy tale lighting, Unreal Engine 5 render, 8k",
    "✨ Magical Fairy Tale 3D Movie": "enchanted 3D fantasy movie render, DreamWorks and Disney style, glowing magic particles, dreamy vibrant colors, 8k",
    "🌸 Studio Ghibli / High-End Anime": "gorgeous Makoto Shinkai and Studio Ghibli anime movie scene, shimmering golden light, expressive eyes, 4k",
    "🎥 Ultra Realistic 4K Cinematic": "photorealistic 8k cinema shot, dramatic golden hour lighting, shallow depth of field, hyper detailed",
    "🧸 Cute Claymation / Toy World": "adorable 3D stop-motion claymation Pixar short film style, soft studio lighting, vibrant miniature world"
}
dims_map = {"9:16 (TikTok / Reels)": (576, 1024), "16:9 (YouTube)": (1024, 576), "1:1 (Instagram)": (768, 768), "4:3 (Classic)": (800, 600)}
angles = ["wide magical establishing shot", "close up portrait shot, smiling", "medium shot, glowing sparkles around", "dramatic angle, enchanted background"]

num_scenes = clips_map[dur]
sec_lbl = dur.split(" ")
w, h = dims_map[rat]

# Smooth Cinema Motion (Zoom In / Zoom Out / Pan) banane wala engine
def create_motion_clip(pil_img, duration=5.0, mode=0):
    base = pil_img.resize((int(w * 1.18), int(h * 1.18)), Image.Resampling.LANCZOS)
    arr = np.array(base)
    bh, bw, _ = arr.shape
    max_dx, max_dy = bw - w, bh - h

    def make_frame(t):
        p = t / duration
        if mode % 3 == 0:  # Smooth Zoom In
            zoom = 1.0 + 0.14 * p
            nw, nh = int(bw / zoom), int(bh / zoom)
            x1, y1 = (bw - nw) // 2, (bh - nh) // 2
            crop = arr[y1:y1+nh, x1:x1+nw]
            return np.array(Image.fromarray(crop).resize((w, h), Image.Resampling.BILINEAR))
        elif mode % 3 == 1:  # Smooth Pan Left to Right
            dx = int(max_dx * p)
            dy = max_dy // 2
            return arr[dy:dy+h, dx:dx+w]
        else:  # Smooth Zoom Out
            zoom = 1.14 - 0.14 * p
            nw, nh = int(bw / zoom), int(bh / zoom)
            x1, y1 = (bw - nw) // 2, (bh - nh) // 2
            crop = arr[y1:y1+nh, x1:x1+nw]
            return np.array(Image.fromarray(crop).resize((w, h), Image.Resampling.BILINEAR))

    return VideoClip(make_frame, duration=duration)

t1, t2, t3 = st.tabs(["📝 Text se Video", "🖼️ Image se Video", f"📚 Library ({len(st.session_state.video_library)})"])

with t1:
    txt = st.text_area("Apni Kahani ya Prompt Likhein (English):", "A beautiful little princess with golden braided hair and big sparkling blue eyes holding a glowing magic wand inside an enchanted crystal castle, cute smile")
    if st.button("Unlimited HD Video Banayein ✨", key="b1") and txt.strip():
        bar = st.progress(0)
        msg = st.empty()
        try:
            client = InferenceClient(api_key=API_KEY) if API_KEY else InferenceClient()
            clips = []
            for i in range(num_scenes):
                msg.info(f"🎨 Scene {i+1}/{num_scenes} ban raha hai...")
                full_p = f"{txt}, {angles[i % 4]}, {styles_map[sty]}"
                img = client.text_to_image(full_p, model="black-forest-labs/FLUX.1-schnell")
                clips.append(create_motion_clip(img, duration=5.0, mode=i))
                bar.progress((i + 1) / num_scenes)

            msg.info("🎞️ Final HD MP4 Video tayyar ho rahi hai...")
            final = concatenate_videoclips(clips, method="compose")
            out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            final.write_videofile(out_path, fps=24, codec="libx264", audio=False, logger=None)
            for c in clips: c.close()

            with open(out_path, "rb") as f: vid = f.read()
            os.remove(out_path)
            msg.empty()

            st.session_state.video_library.insert(0, {"title": txt[:35], "info": f"Text | {sec_lbl}s | {sty} | {rat}", "video": vid})
            st.success(f"🎉 {sec_lbl}s ki Disney HD Video tayyar hai!")
            st.video(vid)
            st.download_button("⬇️ Download MP4", vid, f"disney_{datetime.now().strftime('%H%M%S')}.mp4", "video/mp4", key="d1")
        except Exception as e:
            st.error(f"Error: {e}")

with t2:
    up = st.file_uploader("Apni Tasveer Upload Karein:", type=["jpg", "jpeg", "png"])
    if up: st.image(up, width=250)
    if st.button("Image se HD Video Banayein 🎞️", key="b2") and up:
        try:
            img = Image.open(up).convert("RGB")
            clips = [create_motion_clip(img, duration=5.0, mode=i) for i in range(num_scenes)]
            final = concatenate_videoclips(clips, method="compose")
            out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            final.write_videofile(out_path, fps=24, codec="libx264", audio=False, logger=None)
            for c in clips: c.close()

            with open(out_path, "rb") as f: vid = f.read()
            os.remove(out_path)

            st.session_state.video_library.insert(0, {"title": "Image Animation", "info": f"Image | {sec_lbl}s | {rat}", "video": vid})
            st.success(f"🎉 {sec_lbl}s ki HD Video tayyar hai!")
            st.video(vid)
            st.download_button("⬇️ Download MP4", vid, f"img_{datetime.now().strftime('%H%M%S')}.mp4", "video/mp4", key="d2")
        except Exception as e:
            st.error(f"Error: {e}")

with t3:
    if not st.session_state.video_library: st.info("Abhi koi video nahi bani.")
    for i, item in enumerate(st.session_state.video_library):
        with st.container(border=True):
            st.write(f"**🎬 {i+1}. {item['title']}** ({item['info']})")
            st.video(item["video"])
            st.download_button("⬇️ Download MP4", item["video"], f"lib_{i+1}.mp4", "video/mp4", key=f"ld_{i}")
