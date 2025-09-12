import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

# --------------------------
# ملفات التخزين
# --------------------------
CUSTOMERS_FILE = "customers.json"
USERS_FILE = "users.json"

# --------------------------
# تحميل العملاء
# --------------------------
def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        try:
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_customers(customers):
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

customers = load_customers()

# --------------------------
# تحميل المستخدمين
# --------------------------
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# مستخدم افتراضي
users = load_users()
if not users:
    users = {"Abdallah": {"password": "772001", "lat": "", "lon": ""}}  # المدير
    save_users(users)

# --------------------------
# session_state
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user" not in st.session_state:
    st.session_state.user = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# --------------------------
# إعداد الصفحة
# --------------------------
st.set_page_config(page_title="Baro Life", layout="wide")
st.title("💧 Baro Life ترحب بكم")

# --------------------------
# قبل تسجيل الدخول
# --------------------------
if not st.session_state.logged_in:
    if st.button("Login"):
        st.session_state.show_login = True

# --------------------------
# حقول تسجيل الدخول
# --------------------------
if not st.session_state.logged_in and st.session_state.show_login:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Submit Login"):
        if username in users:
            user_data = users[username]

            if isinstance(user_data, str):
                if user_data == password:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.session_state.user_role = "admin" if username == "Abdallah" else "technician"
                    st.success(f"✅ تم تسجيل الدخول: {username}")
                else:
                    st.error("❌ كلمة المرور غير صحيحة")

            elif isinstance(user_data, dict):
                if user_data.get("password") == password:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.session_state.user_role = "admin" if username == "Abdallah" else "technician"
                    st.success(f"✅ تم تسجيل الدخول: {username}")
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
        else:
            st.error("❌ اسم المستخدم غير موجود")

# --------------------------
# بعد تسجيل الدخول
# --------------------------
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.session_state.show_login = False
        st.success("تم تسجيل الخروج")

    # زر عرض البيانات الخام
    if st.sidebar.button("📂 عرض البيانات الخام للعملاء"):
        st.write(customers)

    # --------------------------
    # خريطة عامة بالعملاء
    # --------------------------
    st.subheader("🗺️ خريطة العملاء")

    locations = []
    for c in customers:
        try:
            if c.get("lat") and c.get("lon"):
                lat = float(str(c["lat"]).strip())
                lon = float(str(c["lon"]).strip())
                locations.append({
                    "name": c["name"],
                    "lat": lat,
                    "lon": lon,
                    "info": f"{c['phone']} - {c.get('governorate','')} - {c.get('line','')}"
                })
        except Exception as e:
            st.warning(f"مشكلة في عميل {c.get('name','غير معروف')}: {e}")

    if locations:
        import pydeck as pdk
        df = pd.DataFrame(locations)

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=10,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=300,
                    pickable=True
                ),
                pdk.Layer(
                    'TextLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_text='name',
                    get_color='[0, 0, 0, 200]',
                    get_size=14,
                    get_alignment_baseline="'bottom'"
                )
            ],
            tooltip={"text": "{name}\n{info}"}
        ))
    else:
        st.info("❌ لا يوجد عملاء مسجل لهم موقع بعد.")

    # --------------------------
    # قائمة لوحة التحكم
    # --------------------------
    st.sidebar.subheader("لوحة التحكم")

    if st.session_state.user_role == "admin":
        menu = st.sidebar.radio("لوحة التحكم", [
            "إضافة العميل",
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "إضافة فني",
            "عرض العملاء على الخريطة"
        ])
    else:
        menu = st.sidebar.radio("لوحة التحكم", [
            "إضافة العميل",
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "عرض العملاء على الخريطة"
        ])
