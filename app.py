import streamlit as st
import json, os
from datetime import datetime
import pandas as pd
import hashlib
import pytz
import folium
from streamlit_folium import st_folium

# ---------------- إعدادات ----------------
st.set_page_config(page_title="Power Life", layout="wide")
TIMEZONE = pytz.timezone("Africa/Cairo")

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
TECH_LOC_FILE = "technicians_locations.json"

# ---------------- دوال ----------------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def valid_coords(c):
    try:
        lat, lon = map(float, c.replace(" ", "").split(","))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False

# ---------------- تحميل البيانات ----------------
users = load_json(USERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, [])
tech_locations = load_json(TECH_LOC_FILE, {})

# إنشاء admin تلقائي
if not any(u["username"] == "admin" for u in users):
    users.append({
        "username": "admin",
        "password": hash_pass("admin123"),
        "role": "admin",
        "full_name": "مدير النظام"
    })
    save_json(USERS_FILE, users)

# ---------------- Session ----------------
if "logged" not in st.session_state:
    st.session_state.logged = False
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- تسجيل دخول ----------------
def login():
    st.title("🏢 Power Life")
    st.subheader("🔐 تسجيل الدخول")

    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u and x["password"] == hash_pass(p)), None)
        if user:
            st.session_state.logged = True
            st.session_state.user = user
            st.success("تم تسجيل الدخول")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")

# ---------------- تحديث موقع الفني ----------------
def update_my_location():
    st.subheader("📍 تحديث موقعي الحالي")
    coords = st.text_input("أدخل إحداثياتك (lat,lon)")

    if st.button("تحديث"):
        if not valid_coords(coords):
            st.error("إحداثيات غير صحيحة")
        else:
            tech_locations[st.session_state.user["username"]] = {
                "coords": coords,
                "time": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")
            }
            save_json(TECH_LOC_FILE, tech_locations)
            st.success("تم تحديث موقعك بنجاح")

# ---------------- الخريطة الموحدة ----------------
def map_page():
    st.header("🗺️ خريطة الفنيين والعملاء")

    m = folium.Map(location=[30.8, 31.0], zoom_start=9)

    # الفنيين
    for tech, info in tech_locations.items():
        if valid_coords(info["coords"]):
            lat, lon = map(float, info["coords"].split(","))
            folium.Marker(
                [lat, lon],
                icon=folium.Icon(color="blue", icon="wrench", prefix="fa"),
                popup=f"👷 {tech}<br>{info['time']}"
            ).add_to(m)

    # العملاء
    for c in customers:
        if c.get("location") and valid_coords(c["location"]):
            lat, lon = map(float, c["location"].split(","))
            folium.Marker(
                [lat, lon],
                icon=folium.Icon(color="red", icon="user"),
                popup=f"""
                🧍 {c['name']}<br>
                📞 {c['phone']}<br>
                <a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" target="_blank">
                الاتجاهات
                </a>
                """
            ).add_to(m)

    st_folium(m, width=1200, height=600)

# ---------------- لوحة التحكم ----------------
def dashboard():
    user = st.session_state.user
    st.sidebar.title("القائمة")

    if user["role"] == "admin":
        choice = st.sidebar.radio("اختر", ["الخريطة", "تسجيل الخروج"])
    else:
        choice = st.sidebar.radio("اختر", ["تحديث موقعي", "الخريطة", "تسجيل الخروج"])

    if choice == "تحديث موقعي":
        update_my_location()
    elif choice == "الخريطة":
        map_page()
    else:
        st.session_state.logged = False
        st.session_state.user = None
        st.rerun()

# ---------------- Main ----------------
if not st.session_state.logged:
    login()
else:
    dashboard()
