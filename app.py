import streamlit as st
import json, os, sqlite3
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk

# --------------------------
# إعداد الصفحة
# --------------------------
st.set_page_config(page_title="Baro Life Global", layout="wide")

# --------------------------
# دعم اللغات
# --------------------------
LANGUAGES = {
    "ar": {
        "welcome": "💧 بارو لايف ترحب بكم - نظام إدارة الصيانة",
        "login": "تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "submit": "دخول",
        "logout": "تسجيل الخروج",
        "dashboard": "لوحة التحكم",
        "add_customer": "➕ إضافة عميل",
        "show_customers": "📋 قائمة العملاء",
        "search": "🔎 البحث عن عميل",
        "reminders": "⏰ تنبيهات الزيارة (30+ يوم)",
        "add_technician": "➕ إضافة فني",
        "map": "🗺️ خريطة العملاء (شوارع وطرق)", 
        "success_login": "✅ تم تسجيل الدخول:",
        "error_login": "❌ اسم المستخدم أو كلمة المرور غير صحيحة",
        "no_customers": "❌ لا يوجد عملاء بعد",
        "view_details": "عرض التفاصيل وسجل الصيانة",
        "add_log": "➕ إضافة سجل صيانة جديد",
        "service_log": "سجل الصيانة السابق",
        "no_log": "لا يوجد سجلات صيانة سابقة لهذا العميل",
        "customer_details": "تفاصيل العميل",
        "back_to_list": "العودة للقائمة",
        "tech_name": "اسم الفني",
        "visit_date": "تاريخ الزيارة",
        "service_type": "نوع الخدمة",
        "status": "الحالة",
        "report": "تقرير الفني",
        "next_visit": "التاريخ المقترح للزيارة التالية",
        "save_log": "حفظ سجل الصيانة",
        "log_saved": "✅ تم حفظ سجل الصيانة بنجاح",
        "open_map": "🗺️ افتح في خرائط جوجل للملاحة",
        "map_new_customer": "🗺️ موقع العميل الجديد على الخريطة",
    },
    "en": {
        "welcome": "💧 Welcome to Baro Life - Maintenance Management System",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "submit": "Submit Login",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "add_customer": "➕ Add Customer",
        "show_customers": "📋 Customers List",
        "search": "🔎 Search Customer",
        "reminders": "⏰ Visit Reminders (30+ days)",
        "add_technician": "➕ Add Technician",
        "map": "🗺️ Customers Map (Streets)", 
        "success_login": "✅ Logged in:",
        "error_login": "❌ Wrong username or password",
        "no_customers": "❌ No customers yet",
        "view_details": "View Details & Maintenance Log",
        "add_log": "➕ Add New Maintenance Log",
        "service_log": "Previous Maintenance Log",
        "no_log": "No previous maintenance logs for this customer",
        "customer_details": "Customer Details",
        "back_to_list": "Back to List",
        "tech_name": "Technician Name",
        "visit_date": "Visit Date",
        "service_type": "Service Type",
        "status": "Status",
        "report": "Technician Report",
        "next_visit": "Suggested Next Visit Date",
        "save_log": "Save Maintenance Log",
        "open_map": "🗺️ Open in Google Maps for Navigation",
        "map_new_customer": "🗺️ New Customer Location on Map",
    }
}

# --------------------------
# اختيار اللغة
# --------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "ar"

lang = st.sidebar.radio("🌐 Language / اللغة", ["ar", "en"], index=0)
st.session_state.lang = lang
T = LANGUAGES[lang]

# --------------------------
# قاعدة البيانات
# --------------------------
DB_FILE = "barolife.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 role TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS customers(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 phone TEXT,
                 lat REAL,
                 lon REAL,
                 location TEXT,
                 notes TEXT,
                 category TEXT,
                 region TEXT,
                 last_visit TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS maintenance_log(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 customer_id INTEGER,
                 technician_name TEXT,
                 visit_date TEXT,
                 service_type TEXT,
                 status TEXT,
                 report TEXT,
                 next_visit_date TEXT,
                 FOREIGN KEY(customer_id) REFERENCES customers(id))""")
    conn.commit()
    conn.close()

init_db()

def add_user(username, password, role="technician"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def add_customer(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO customers(name,phone,lat,lon,location,notes,category,region,last_visit)
                 VALUES (?,?,?,?,?,?,?,?,?)""",
              (data["name"], data["phone"], data["lat"], data["lon"], data["location"],
               data["notes"], data["category"], data["region"], data["last_visit"]))
    conn.commit()
    conn.close()

def get_customers():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM customers", conn)
    conn.close()
    return df

def get_customer_by_id(customer_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    row = c.fetchone()
    
    if row:
        columns = [desc[0] for desc in c.description]
        customer_data = dict(zip(columns, row))
    else:
        customer_data = None
        
    conn.close()
    return customer_data

def add_maintenance_log(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO maintenance_log(customer_id, technician_name, visit_date, service_type, status, report, next_visit_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (data["customer_id"], data["technician_name"], data["visit_date"],
               data["service_type"], data["status"], data["report"], data["next_visit_date"]))
    c.execute("UPDATE customers SET last_visit=? WHERE id=?", (data["visit_date"], data["customer_id"]))
    conn.commit()
    conn.close()

def get_customer_maintenance_log(customer_id):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM maintenance_log WHERE customer_id=?", conn, params=(customer_id,))
    conn.close()
    return df

# --------------------------
# تعديل الخريطة (أقمار صناعية)
# --------------------------
def render_customer_map(df, T):
    df_map = df.dropna(subset=["lat", "lon"]).copy()
    default_lat = 30.0 
    default_lon = 31.2
    default_zoom = 5 

    if not df_map.empty:
        center_lat = df_map["lat"].mean()
        center_lon = df_map["lon"].mean()
        initial_zoom = 10 
    else:
        center_lat = default_lat
        center_lon = default_lon
        initial_zoom = default_zoom

    layers = []
    if not df_map.empty:
        df_map.loc[:, 'tooltip_text'] = df_map.apply(lambda row: f"{row['name']} - {row['region']}\nآخر زيارة: {row['last_visit']}", axis=1)
        ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-data/location-pin.json"
        icon_data = {"url": ICON_URL,"width": 128,"height": 128,"anchorY": 128}
        df_map['icon_data'] = [icon_data] * len(df_map)
        
        layers.append(pdk.Layer(
            'IconLayer',
            data=df_map,
            get_icon='icon_data',
            get_position='[lon, lat]',
            get_size=10,
            size_scale=6,
            get_color='[255, 0, 0]',
            pickable=True
        ))
    
    st.pydeck_chart(pdk.Deck(
        # التغيير هنا 👇
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=initial_zoom,
            pitch=0,
        ),
        layers=layers,
        tooltip={"text": "{tooltip_text}"} if not df_map.empty else None
    ))
    
    if df.empty:
        st.info("💡 يتم عرض الخريطة الآن على الموقع الافتراضي. لا توجد بيانات عملاء مسجلة.")
    elif df_map.empty and not df.empty:
        st.warning("⚠️ لديك عملاء، لكن لا توجد إحداثيات GPS مسجلة لهم.")

# --------------------------
# مستخدم افتراضي
# --------------------------
add_user("Abdallah", "772001", "admin")
add_user("Mohamed", "12345", "technician") # فني تجريبي

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
if "view_customer_id" not in st.session_state:
    st.session_state.view_customer_id = None
if "customers_df" not in st.session_state:
    st.session_state.customers_df = get_customers()

# --------------------------
# واجهة تفاصيل العميل (نفس الكود السابق)
# --------------------------
# ... (هنا يفضل نسيب باقي الكود زي ما هو بدون تغيير)
