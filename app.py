import streamlit as st
import json, os, re
from datetime import datetime
import pandas as pd
import hashlib
import pytz
import folium
from streamlit_folium import st_folium

# ------------------ إعدادات التطبيق ------------------
st.set_page_config(
    page_title="Power Life",
    page_icon="🏢",
    layout="wide"
)

TIMEZONE = pytz.timezone("Africa/Cairo")
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# ------------------ دوال مساعدة ------------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def valid_coords(c):
    try:
        lat, lon = map(float, c.replace(" ", "").split(","))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False

# ------------------ تحميل البيانات ------------------
users = load_json(USERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, [])

# ------------------ إنشاء admin تلقائي ------------------
if not any(u["username"] == "admin" for u in users):
    users.append({
        "username": "admin",
        "password": hash_password("admin123"),
        "role": "admin",
        "full_name": "مدير النظام"
    })
    save_json(USERS_FILE, users)

# ------------------ Session ------------------
if "logged" not in st.session_state:
    st.session_state.logged = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ------------------ تسجيل الدخول ------------------
def login():
    st.title("🏢 Power Life")
    st.subheader("🔐 تسجيل الدخول")

    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        hp = hash_password(p)
        user = next((x for x in users if x["username"] == u and x["password"] == hp), None)
        if user:
            st.session_state.logged = True
            st.session_state.user = user
            st.session_state.page = "dashboard"
            st.success("تم تسجيل الدخول")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")

# ------------------ لوحة التحكم ------------------
def dashboard():
    st.sidebar.title("القائمة")

    choice = st.sidebar.radio(
        "اذهب إلى",
        ["لوحة التحكم", "إضافة عميل", "الخريطة", "تسجيل الخروج"]
    )

    if choice == "لوحة التحكم":
        home()
    elif choice == "إضافة عميل":
        add_customer()
    elif choice == "الخريطة":
        map_page()
    else:
        logout()

# ------------------ الصفحة الرئيسية ------------------
def home():
    st.header("📊 لوحة التحكم")

    col1, col2 = st.columns(2)
    col1.metric("عدد العملاء", len(customers))
    col2.metric("المستخدم الحالي", st.session_state.user["username"])

    if customers:
        st.dataframe(pd.DataFrame(customers)[["name", "phone", "category"]])

# ------------------ إضافة عميل ------------------
def add_customer():
    global customers
    st.header("➕ إضافة عميل")

    with st.form("add"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("الهاتف")
        category = st.selectbox("التصنيف", ["منزل", "شركة", "مصنع"])
        location = st.text_input("الإحداثيات (lat,lon)")
        submit = st.form_submit_button("حفظ")

        if submit:
            if not name or not phone:
                st.error("أكمل البيانات")
            elif location and not valid_coords(location):
                st.error("إحداثيات خطأ")
            else:
                customers.append({
                    "id": max([c["id"] for c in customers], default=0) + 1,
                    "name": name,
                    "phone": phone,
                    "category": category,
                    "location": location
                })
                save_json(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ")
                st.rerun()

# ------------------ الخريطة الاحترافية ------------------
def map_page():
    st.header("🗺️ خريطة العملاء")

    m = folium.Map(location=[30.8, 31.0], zoom_start=9, tiles="OpenStreetMap")

    for c in customers:
        if c.get("location") and valid_coords(c["location"]):
            lat, lon = map(float, c["location"].split(","))
            folium.Marker(
                [lat, lon],
                popup=f"""
                <b>{c['name']}</b><br>
                {c['phone']}<br>
                <a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" target="_blank">
                الاتجاهات
                </a>
                """,
                icon=folium.Icon(color="blue", icon="user")
            ).add_to(m)

    st_folium(m, width=1200, height=600)

# ------------------ تسجيل خروج ------------------
def logout():
    st.session_state.logged = False
    st.session_state.user = None
    st.session_state.page = "login"
    st.rerun()

# ------------------ Main ------------------
if not st.session_state.logged:
    login()
else:
    dashboard()
