import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.set_page_config(page_title="خريطة العملاء", layout="wide")

# -----------------------------
#   بيانات العملاء
# -----------------------------
clients = [
    {"name": "عميل 1", "lat": 30.796, "lon": 31.128},
    {"name": "عميل 2", "lat": 30.799, "lon": 31.135},
    {"name": "عميل 3", "lat": 30.803, "lon": 31.140},
]

# -----------------------------
#   تحديد موقع المستخدم
# -----------------------------
st.sidebar.title("📍 موقعك الحالي")
user_lat = st.sidebar.number_input("خط العرض", value=30.800)
user_lon = st.sidebar.number_input("خط الطول", value=31.130)

# -----------------------------
#   إنشاء خريطة Google Style
# -----------------------------
tiles_google = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"

m = folium.Map(
    location=[user_lat, user_lon],
    zoom_start=14,
    tiles=tiles_google,
    attr="Google Maps"
)

# -----------------------------
#   Markers العملاء
# -----------------------------
for c in clients:
    popup_html = f"""
    <b>{c['name']}</b><br>
    <a href="https://www.google.com/maps/dir/{user_lat},{user_lon}/{c['lat']},{c['lon']}" target="_blank">
    👉 الاتجاهات
    </a>
    """
    folium.Marker(
        [c["lat"], c["lon"]],
        tooltip=c["name"],
        popup=popup_html,
        icon=folium.Icon(color="red", icon="location")
    ).add_to(m)

# -----------------------------
#   Marker لموقع المستخدم
# -----------------------------
folium.Marker(
    [user_lat, user_lon],
    tooltip="موقعك الحالي",
    icon=folium.Icon(color="blue", icon="user")
).add_to(m)

# -----------------------------
#   عرض الخريطة
# -----------------------------
st_map = st_folium(m, width=800, height=550)
