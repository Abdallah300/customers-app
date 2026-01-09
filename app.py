import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np

st.set_page_config(page_title="Power Life - Voice Chat", layout="wide")

# ----------------- Session -----------------
if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------- تسجيل الاسم -----------------
st.title("🎙️ Power Life – الدردشة الصوتية")

if not st.session_state.username:
    st.subheader("👤 أدخل اسمك للدخول")
    name = st.text_input("اسم المستخدم")

    if st.button("دخول"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
        else:
            st.warning("من فضلك أدخل اسمك")
else:
    st.success(f"مرحباً {st.session_state.username}")

    # ----------------- اختيار الغرفة -----------------
    st.sidebar.title("🎧 لوحة التحكم")
    room = st.sidebar.selectbox(
        "اختر الغرفة الصوتية",
        ["غرفة الإدارة", "غرفة الفنيين", "غرفة الدعم"]
    )

    st.sidebar.markdown(f"**🟢 الغرفة الحالية:** {room}")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state.username = ""
        st.rerun()

    # ----------------- معالج الصوت -----------------
    class AudioProcessor(AudioProcessorBase):
        def recv(self, frame):
            audio = frame.to_ndarray()
            return frame  # صوت مباشر بدون تعديل

    # ----------------- البث الصوتي -----------------
    st.markdown("## 🔊 الدردشة الصوتية المباشرة")
    st.info("اسمح للمتصفح باستخدام الميكروفون")

    webrtc_streamer(
        key=f"voice-{room}",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={
            "audio": True,
            "video": False
        },
        async_processing=True,
    )

    # ----------------- معلومات -----------------
    st.markdown("---")
    st.markdown("### ℹ️ تعليمات")
    st.markdown("""
    - هذه دردشة صوتية مباشرة (Live)
    - لا يتم تسجيل أي صوت
    - كل غرفة مستقلة بصوتها
    - تعمل على الموبايل والكمبيوتر
    """)
