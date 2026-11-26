import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io
import os

# Page ki settings
st.set_page_config(page_title="AI Video Studio", page_icon="🎬", layout="centered")

# App ka Title aur Description
st.title("🎬 AI Video Generator Studio")
st.write("Text prompt ya kisi bhi tasveer (Image) se bilkul FREE AI video banayein!")

# Yeh line Hugging Face ki Secrets se aapki key khud utha legi
API_KEY = os.environ.get("HF_TOKEN")

# App ke 2 Tabs: Text-to-Video aur Image-to-Video
tab1, tab2 = st.tabs(["📝 Text se Video (Text-to-Video)", "🖼️ Image se Video (Image-to-Video)"])

# --- TAB 1: TEXT TO VIDEO ---
with tab1:
    st.subheader("Likhein ke aap kaisi video chahte hain")
    text_prompt = st.text_area(
        "Video Prompt (English mein likhein):",
        placeholder="A cinematic drone shot of mountains at sunset, 4k realistic..."
    )
    
    if st.button("Text se Video Banayein 🎥", key="btn_text"):
        if not text_prompt:
            st.warning("⚠️ Meharbani karke pehle prompt likhein.")
        else:
            with st.spinner("AI aapki video tayyar kar raha hai... Is mein 1 se 2 minute lag sakte hain."):
                try:
                    client = InferenceClient(token=API_KEY)
                    video_bytes = client.text_to_video(
                        text_prompt,
                        model="ali-vilab/text-to-video-ms-1.7b"
                    )
                    st.success("🎉 Video tayyar hai!")
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ Video Download Karein",
                        data=video_bytes,
                        file_name="ai_text_video.mp4",
                        mime="video/mp4"
                    )
                except Exception as e:
                    st.error("Server par abhi load zyada hai, 1 minute baad dobara koshish karein.")

# --- TAB 2: IMAGE TO VIDEO ---
with tab2:
    st.subheader("Apni tasveer upload karein aur us mein harkat (motion) dalein")
    uploaded_file = st.file_uploader("Tasveer chunein (JPG ya PNG):", type=["jpg", "jpeg", "png"])
    img_prompt = st.text_input(
        "Tasveer mein kya harkat honi chahiye? (English mein):",
        placeholder="The person is smiling and waving hand, wind blowing..."
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Upload ki gayi tasveer", width=300)
        
    if st.button("Image se Video Banayein 🎞️", key="btn_img"):
        if uploaded_file is None:
            st.warning("⚠️ Pehle koi tasveer upload karein.")
        else:
            with st.spinner("Tasveer ko video mein badla ja raha hai... Thora intezar karein."):
                try:
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    client = InferenceClient(token=API_KEY)
                    video_bytes = client.image_to_video(
                        image=img_bytes,
                        prompt=img_prompt if img_prompt else "smooth cinematic motion",
                        model="stabilityai/stable-video-diffusion-img2vid-xt"
                    )
                    st.success("🎉 Image se video ban gayi hai!")
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ Video Download Karein",
                        data=video_bytes,
                        file_name="ai_image_video.mp4",
                        mime="video/mp4"
                    )
                except Exception as e:
                    st.error("Server par abhi load zyada hai, 1 minute baad dobara koshish karein.")
