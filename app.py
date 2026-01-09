import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import uuid

st.set_page_config(page_title="Voice Chat App", layout="centered")

# ---------------- Session ----------------
if "username" not in st.session_state:
    st.session_state.username = ""
if "room" not in st.session_state:
    st.session_state.room = ""
if "mute" not in st.session_state:
    st.session_state.mute = False

# ---------------- الصفحة الرئيسية ----------------
st.title("🎙️ تطبيق دردشة صوتية مباشر")

# ---------------- تسجيل الدخول ----------------
if not st.session_state.username:
    st.subheader("👤 تسجيل الدخول")

    name = st.text_input("اسم المستخدم")

    if st.button("دخول"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
        else:
            st.warning("اكتب اسمك")

# ---------------- بعد الدخول ----------------
else:
    st.success(f"مرحباً {st.session_state.username}")

    st.sidebar.title("🎛️ لوحة التحكم")

    # ---------- اختيار الغرفة ----------
    room_type = st.sidebar.radio(
        "نوع الغرفة",
        ["غرفة عامة", "غرفة خاصة"]
    )

    if room_type == "غرفة عامة":
        room_name = st.sidebar.selectbox(
            "اختر الغرفة",
            ["غرفة عامة", "غرفة دعم", "غرفة فنيين"]
        )
        st.session_state.room = room_name

    else:
        private_room = st.sidebar.text_input("أدخل رقم الغرفة")
        if st.sidebar.button("إنشاء غرفة جديدة"):
            private_room = str(uuid.uuid4())[:8]
            st.session_state.room = private_room
            st.sidebar.success(f"تم إنشاء الغرفة: {private_room}")

        if private_room:
            st.session_state.room = private_room

    # ---------- كتم الصوت ----------
    st.session_state.mute = st.sidebar.toggle("🔇 كتم المايك")

    # ---------- تسجيل خروج ----------
    if st.sidebar.button("🚪 تسجيل خروج"):
        st.session_state.username = ""
        st.session_state.room = ""
        st.rerun()

    # ---------------- الدردشة الصوتية ----------------
    if st.session_state.room:
        st.markdown(f"## 🎧 الغرفة: `{st.session_state.room}`")
        st.info("اسمح باستخدام الميكروفون")

        class AudioProcessor(AudioProcessorBase):
            def recv(self, frame):
                if st.session_state.mute:
                    return None
                return frame

        webrtc_streamer(
            key=f"voice-{st.session_state.room}",
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={
                "audio": True,
                "video": False
            },
        )

        st.markdown("---")
        st.markdown("""
        ### ℹ️ تعليمات
        - الصوت مباشر (Live)
        - لا يتم تسجيل أي صوت
        - الغرفة الخاصة تدخلها بنفس الرقم
        - كتم المايك من لوحة التحكم
        """)

    else:
        st.warning("اختر أو أنشئ غرفة أولاً")
