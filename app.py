import streamlit as st
import json
import os

# ---------------------------
# تحميل بيانات المستخدمين
# ---------------------------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ---------------------------
# حفظ بيانات المستخدمين
# ---------------------------
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ---------------------------
# واجهة تسجيل الدخول
# ---------------------------
def login_page():
    st.title("🏢 Power Life ترحب بكم")
    st.subheader("🔑 تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        users = load_users()
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)

        if user:
            st.session_state["logged"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# ---------------------------
# لوحة التحكم
# ---------------------------
def dashboard():
    st.title(f"✅ مرحبا {st.session_state['username']}")
    st.subheader("لوحة التحكم")

    st.success("تم تسجيل الدخول بنجاح!")

    if st.button("تسجيل الخروج"):
        st.session_state.clear()
        st.experimental_rerun()

# ---------------------------
# تشغيل التطبيق
# ---------------------------
if "logged" not in st.session_state:
    st.session_state["logged"] = False

if st.session_state["logged"]:
    dashboard()
else:
    login_page()
