import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
import tempfile, os
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips

st.set_page_config(page_title="AI Disney Studio Pro", page_icon="👑", layout="centered")
st.title("👑 AI Disney & Video Studio Pro")
st.write("Pixar/Disney 3D Cartoon aur 5s se 60s tak ki videos bilkul FREE banayein!")

if "video_library" not in st.session_state:
    st.session_state.video_library = []

def get_mp4(res):
    if isinstance(res, str): return res
    if isinstance(res, dict): return res.get("video") or res.get("url") or list(res.values())[0]
    if isinstance(res, (list, tuple)):
        for x in res:
            p = get_mp4(x)
            if isinstance(p, str) and (p.endswith(".mp4") or os.path.exists(p)): return p
        return get_mp4(res[0])
    return str(res)

with st.sidebar:
    st.header("⚙️ Studio Settings")
    dur = st.selectbox("⏱️ Video Length:", ["5 Seconds (1 Scene)", "10 Seconds (2 Scenes)", "15 Seconds (3 Scenes)", "30 Seconds (6 Scenes)", "60 Seconds (12 Scenes)"])
    rat = st.selectbox("📐 Video Ratio:", ["9:16 (TikTok / Reels)", "16:9 (YouTube)", "1:1 (Instagram)", "4:3 (Classic)"])
    sty = st.selectbox("🎨 Video Style:", ["👑 Disney / Pixar 3D Princess", "✨ Magical Fairy Tale 3D", "🌸 Studio Ghibli Anime", "🎥 Ultra Realistic 4K", "🧸 Cute Claymation"])
    st.info(f"📚 Saved Videos: **{len(st.session_state.video_library)}**")

clips_map = {"5 Seconds (1 Scene)": 1, "10 Seconds (2 Scenes)": 2, "15 Seconds (3 Scenes)": 3, "30 Seconds (6 Scenes)": 6, "60 Seconds (12 Scenes)": 12}
styles_map = {
    "👑 Disney / Pixar 3D Princess": "masterpiece 3D Disney Pixar animation, ultra cute character, big glossy expressive eyes, magical lighting, 8k Unreal Engine 5 render",
    "✨ Magical Fairy Tale 3D": "enchanted 3D fantasy animation, DreamWorks Disney render, glowing sparkles, vibrant colors, 8k",
    "🌸 Studio Ghibli Anime": "gorgeous Studio Ghibli Makoto Shinkai anime, shimmering light, detailed face, 4k anime movie",
    "🎥 Ultra Realistic 4K": "photorealistic 8k cinema camera, golden hour lighting, ultra detailed textures, smooth motion",
    "🧸 Cute Claymation": "adorable 3D stop-motion claymation style, soft studio lighting, miniature toy world"
}
dims_map = {"9:16 (TikTok / Reels)": (480, 832), "16:9 (YouTube)": (832, 480), "1:1 (Instagram)": (640, 640), "4:3 (Classic)": (640, 480)}
scenes = ["wide establishing shot", "close up portrait, smiling", "medium shot, magical sparkles", "cinematic camera pan"]

num_clips = clips_map[dur]
sec_lbl = dur.split(" ")[0]
w, h = dims_map[rat]

def make_video(prompt_txt, img_path=None):
    bar = st.progress(0)
    msg = st.empty()
    files = []
    client = Client("Lightricks/ltx-video-distilled")
    for i in range(num_clips):
        msg.info(f"🎬 Scene {i+1}/{num_clips} ban raha hai... (Thora intezar karein)")
        fp = f"{prompt_txt}, {scenes[i % 4]}, {styles_map[sty]}"
        res = client.predict(
            prompt=fp, negative_prompt="worst quality, blurry, ugly, deformed, jittery, watermark",
            input_image_filepath=handle_file(img_path) if img_path else None, input_video_filepath=None,
            height_ui=h, width_ui=w, mode="image-to-video" if img_path else "text-to-video",
            duration_ui=5.0, ui_frames_to_use=25, seed_ui=42+i, randomize_seed=True,
            ui_guidance_scale=4.5, improve_texture_flag=True,
            api_name="/image_to_video" if img_path else "/text_to_video"
        )
        files.append(get_mp4(res))
        bar.progress((i + 1) / num_clips)
    msg.info("🎞️ Final HD MP4 tayyar ho rahi hai...")
    if len(files) == 1:
        out_path = files[0]
    else:
        clips = [VideoFileClip(p) for p in files]
        final = concatenate_videoclips(clips, method="compose")
        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out_path, codec="libx264", audio=False, logger=None)
        for c in clips: c.close()
    msg.empty()
    with open(out_path, "rb") as f: return f.read()

t1, t2, t3 = st.tabs(["📝 Text se Video", "🖼️ Image se Video", f"📚 Library ({len(st.session_state.video_library)})"])

with t1:
    txt = st.text_area("Video Prompt (English):", "A beautiful little princess with golden braided hair and big sparkling blue eyes holding a glowing magic wand in a crystal castle, cute smile")
    if st.button("High-Quality Video Banayein ✨", key="b1") and txt.strip():
        try:
            vid = make_video(txt)
            st.session_state.video_library.insert(0, {"title": txt[:35], "info": f"Text | {sec_lbl}s | {sty} | {rat}", "video": vid})
            st.success(f"🎉 {sec_lbl}s ki HD Video tayyar hai!")
            st.video(vid)
            st.download_button("⬇️ Download MP4", vid, f"disney_{datetime.now().strftime('%H%M%S')}.mp4", "video/mp4", key="d1")
        except Exception as e:
            st.error(f"Server busy hai, 30s baad dubara click karein: {e}")

with t2:
    up = st.file_uploader("Tasveer upload karein:", type=["jpg", "jpeg", "png"])
    itxt = st.text_input("Harkat likhein (English):", "Cute princess blinking big sparkling eyes, gentle smile, glowing magic wind")
    if up: st.image(up, width=250)
    if st.button("Image se Video Banayein 🎞️", key="b2") and up:
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
            Image.open(up).convert("RGB").resize((w, h)).save(tmp)
            vid = make_video(itxt, tmp)
            os.remove(tmp)
            st.session_state.video_library.insert(0, {"title": itxt[:35], "info": f"Image | {sec_lbl}s | {sty} | {rat}", "video": vid})
            st.success(f"🎉 {sec_lbl}s ki HD Video tayyar hai!")
            st.video(vid)
            st.download_button("⬇️ Download MP4", vid, f"disney_img_{datetime.now().strftime('%H%M%S')}.mp4", "video/mp4", key="d2")
        except Exception as e:
            st.error(f"Server busy hai, 30s baad dubara click karein: {e}")

with t3:
    if not st.session_state.video_library: st.info("Abhi koi video nahi bani.")
    for i, item in enumerate(st.session_state.video_library):
        with st.container(border=True):
            st.write(f"**🎬 {i+1}. {item['title']}** ({item['info']})")
            st.video(item["video"])
            st.download_button("⬇️ Download MP4", item["video"], f"lib_{i+1}.mp4", "video/mp4", key=f"ld_{i}")
