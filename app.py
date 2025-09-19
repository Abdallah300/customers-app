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
        "welcome": "💧 بارو لايف ترحب بكم",
        "login": "تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "submit": "دخول",
        "logout": "تسجيل الخروج",
        "dashboard": "لوحة التحكم",
        "add_customer": "➕ إضافة عميل",
        "show_customers": "📋 قائمة العملاء",
        "search": "🔎 البحث عن عميل",
        "reminders": "⏰ العملاء المطلوب زيارتهم (30+ يوم)",
        "add_technician": "➕ إضافة فني",
        "map": "🗺️ خريطة العملاء (قمر صناعي)",
        "success_login": "✅ تم تسجيل الدخول:",
        "error_login": "❌ اسم المستخدم أو كلمة المرور غير صحيحة",
        "no_customers": "❌ لا يوجد عملاء بعد",
    },
    "en": {
        "welcome": "💧 Welcome to Baro Life",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "submit": "Submit Login",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "add_customer": "➕ Add Customer",
        "show_customers": "📋 Customers List",
        "search": "🔎 Search Customer",
        "reminders": "⏰ Customers to Visit (30+ days)",
        "add_technician": "➕ Add Technician",
        "map": "🗺️ Customers Map (Satellite)",
        "success_login": "✅ Logged in:",
        "error_login": "❌ Wrong username or password",
        "no_customers": "❌ No customers yet",
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

# --------------------------
# مستخدم افتراضي
# --------------------------
add_user("Abdallah", "772001", "admin")

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
# واجهة
# --------------------------
st.title(T["welcome"])

# قبل تسجيل الدخول
if not st.session_state.logged_in:
    if st.button(T["login"]):
        st.session_state.show_login = True

# حقول تسجيل الدخول
if not st.session_state.logged_in and st.session_state.show_login:
    username = st.text_input(T["username"])
    password = st.text_input(T["password"], type="password")
    if st.button(T["submit"]):
        role = check_user(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.user_role = role
            st.success(f"{T['success_login']} {username}")
        else:
            st.error(T["error_login"])

# بعد تسجيل الدخول
if st.session_state.logged_in:
    if st.sidebar.button(T["logout"]):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.session_state.show_login = False
        st.success("تم تسجيل الخروج")

    st.sidebar.subheader(T["dashboard"])

    if st.session_state.user_role == "admin":
        menu = st.sidebar.radio(T["dashboard"], [
            T["add_customer"],
            T["show_customers"],
            T["search"],
            T["reminders"],
            T["add_technician"],
            T["map"]
        ])
    else:
        menu = st.sidebar.radio(T["dashboard"], [
            T["show_customers"],
            T["search"],
            T["reminders"],
            T["map"]
        ])

    # إضافة عميل
    if menu == T["add_customer"]:
        st.subheader(T["add_customer"])
        with st.form("add_form"):
            name = st.text_input("Name / الاسم")
            phone = st.text_input("Phone / التليفون")
            lat = st.text_input("Latitude")
            lon = st.text_input("Longitude")
            region = st.text_input("Region / المنطقة")
            location = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""
            notes = st.text_area("Notes / ملاحظات")
            category = st.selectbox("Category / التصنيف", ["Home / منزل", "Company / شركة", "School / مدرسة"])
            last_visit = st.date_input("Last Visit / آخر زيارة", datetime.today())
            if st.form_submit_button("Save / حفظ"):
                add_customer({
                    "name": name,
                    "phone": phone,
                    "lat": float(lat) if lat else None,
                    "lon": float(lon) if lon else None,
                    "location": location,
                    "notes": notes,
                    "category": category,
                    "region": region,
                    "last_visit": str(last_visit)
                })
                st.success("✅ تم الحفظ")

    # عرض العملاء
    elif menu == T["show_customers"]:
        st.subheader(T["show_customers"])
        df = get_customers()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info(T["no_customers"])

    # البحث
    elif menu == T["search"]:
        st.subheader(T["search"])
        keyword = st.text_input("Search / بحث")
        df = get_customers()
        if keyword:
            results = df[df.apply(lambda r: keyword.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
            else:
                st.warning("لا يوجد نتائج / No results")

    # التذكير
    elif menu == T["reminders"]:
        st.subheader(T["reminders"])
        df = get_customers()
        if not df.empty:
            today = datetime.today()
            df["last_visit"] = pd.to_datetime(df["last_visit"], errors="coerce")
            reminders = df[df["last_visit"].notna() & (today - df["last_visit"] >= timedelta(days=30))]
            if not reminders.empty:
                st.dataframe(reminders)
            else:
                st.success("✅ لا يوجد عملاء يحتاجون زيارة")
        else:
            st.info(T["no_customers"])

    # إضافة فني
    elif menu == T["add_technician"] and st.session_state.user_role == "admin":
        st.subheader(T["add_technician"])
        new_user = st.text_input("اسم المستخدم / Username")
        new_pass = st.text_input("كلمة السر / Password", type="password")
        if st.button("حفظ الفني / Save"):
            if new_user and new_pass:
                add_user(new_user, new_pass, "technician")
                st.success(f"تم إضافة الفني {new_user} ✅")

    # الخريطة
    elif menu == T["map"]:
        st.subheader(T["map"])
        df = get_customers()
        if not df.empty:
            df_map = df.dropna(subset=["lat", "lon"])
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/satellite-v9',
                initial_view_state=pdk.ViewState(
                    latitude=df_map["lat"].mean(),
                    longitude=df_map["lon"].mean(),
                    zoom=10,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df_map,
                        get_position='[lon, lat]',
                        get_color='[255, 0, 0, 200]',
                        get_radius=300,
                        pickable=True
                    )
                ],
                tooltip={"text": "{name} - {region}"}
            ))
        else:
            st.info(T["no_customers"])

# ✅ هذا التطبيق الآن عالمي: لغات + مناطق + قاعدة بيانات + تسجيل دخول آمن
