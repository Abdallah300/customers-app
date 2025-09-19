import streamlit as st import sqlite3 from datetime import datetime, timedelta import pandas as pd import os import hashlib import pydeck as pdk

---------------------------------

إعداد قاعدة البيانات (SQLite)

---------------------------------

DB_FILE = "app.db"

def get_db_connection(): conn = sqlite3.connect(DB_FILE, check_same_thread=False) conn.row_factory = sqlite3.Row return conn

def init_db(): conn = get_db_connection() c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    company_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    lat REAL,
    lon REAL,
    location TEXT,
    notes TEXT,
    category TEXT,
    last_visit TEXT,
    company_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
''')

conn.commit()
conn.close()

---------------------------------

أدوات التشفير البسيطة لكلمة المرور

---------------------------------

SALT = "streamlit_app_salt_v1"  # يمكنك تغييره لمزيد من الأمان

def hash_password(password: str) -> str: return hashlib.sha256((password + SALT).encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool: return hash_password(password) == password_hash

---------------------------------

وظائف قاعدة البيانات

---------------------------------

def create_company(name: str): conn = get_db_connection() c = conn.cursor() c.execute("INSERT OR IGNORE INTO companies (name, created_at) VALUES (?,?)", (name, datetime.utcnow().isoformat())) conn.commit() conn.close()

def get_companies(): conn = get_db_connection() c = conn.cursor() c.execute("SELECT * FROM companies ORDER BY name") rows = c.fetchall() conn.close() return rows

def get_company_by_id(company_id): conn = get_db_connection() c = conn.cursor() c.execute("SELECT * FROM companies WHERE id = ?", (company_id,)) row = c.fetchone() conn.close() return row

def create_user(username: str, password: str, role: str, company_id: int = None): conn = get_db_connection() c = conn.cursor() pw_hash = hash_password(password) created_at = datetime.utcnow().isoformat() c.execute("INSERT INTO users (username, password_hash, role, company_id, created_at) VALUES (?,?,?,?,?)", (username, pw_hash, role, company_id, created_at)) conn.commit() conn.close()

def find_user(username: str, company_id: int = None): conn = get_db_connection() c = conn.cursor() if company_id: c.execute("SELECT * FROM users WHERE username = ? AND company_id = ?", (username, company_id)) else: c.execute("SELECT * FROM users WHERE username = ?", (username,)) row = c.fetchone() conn.close() return row

def authenticate(username: str, password: str, company_id: int = None): user = find_user(username, company_id) if not user: return None if verify_password(password, user["password_hash"]): return user return None

def add_customer(company_id: int, name: str, phone: str, lat: float, lon: float, notes: str, category: str, last_visit: str): conn = get_db_connection() c = conn.cursor() location = f"https://www.google.com/maps?q={lat},{lon}" if lat is not None and lon is not None else "" created_at = datetime.utcnow().isoformat() c.execute( "INSERT INTO customers (name, phone, lat, lon, location, notes, category, last_visit, company_id, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", (name, phone, lat, lon, location, notes, category, last_visit, company_id, created_at) ) conn.commit() conn.close()

def get_customers(company_id: int): conn = get_db_connection() c = conn.cursor() c.execute("SELECT * FROM customers WHERE company_id = ? ORDER BY name", (company_id,)) rows = c.fetchall() conn.close() return rows

def search_customers(company_id: int, keyword: str): conn = get_db_connection() c = conn.cursor() like = f"%{keyword}%" c.execute("SELECT * FROM customers WHERE company_id = ? AND (name LIKE ? OR phone LIKE ?) ORDER BY name", (company_id, like, like)) rows = c.fetchall() conn.close() return rows

---------------------------------

إعداد واجهة Streamlit

---------------------------------

init_db()

st.set_page_config(page_title="Multi-Company CRM", layout="wide") st.title("💧 Multi-Company CRM - إدارة عملاء وفِرق الصيانة")

--------------------------

session_state defaults

--------------------------

if "logged_in" not in st.session_state: st.session_state.logged_in = False if "user" not in st.session_state: st.session_state.user = None if "user_role" not in st.session_state: st.session_state.user_role = None if "company_id" not in st.session_state: st.session_state.company_id = None if "show_login" not in st.session_state: st.session_state.show_login = False

--------------------------

شريط جانبي: اختيار الشركة / تسجيل

--------------------------

st.sidebar.header("إعداد الشركة / الدخول") companies = get_companies() company_names = [c["name"] for c in companies] company_choice = None

if companies: company_choice = st.sidebar.selectbox("اختر الشركة", ["-- جديدة --"] + company_names) else: st.sidebar.info("لا توجد شركات مسجلة بعد. أنشئ شركة جديدة أدناه.")

تسجيل شركة جديدة

with st.sidebar.expander("إنشاء شركة جديدة", expanded=False): new_company_name = st.text_input("اسم الشركة الجديدة") if st.button("إنشاء شركة"): if new_company_name.strip(): create_company(new_company_name.strip()) st.experimental_rerun()

st.sidebar.markdown("---")

شكل تسجيل الدخول

st.sidebar.subheader("تسجيل / دخول") col1, col2 = st.sidebar.columns([2,1])

with col1: username = st.text_input("اسم المستخدم", key="username_input") password = st.text_input("كلمة المرور", type="password", key="password_input") with col2: role_login = st.selectbox("دور الدخول", ["admin","technician"], index=0)

اختيار الشركة للدخول (لو اختار من القائمة)

selected_company_id = None if company_choice and company_choice != "-- جديدة --": # احصل على id للشركة for c in companies: if c["name"] == company_choice: selected_company_id = c["id"] break

if st.sidebar.button("دخول"): user_row = authenticate(username, password, selected_company_id) if user_row: st.session_state.logged_in = True st.session_state.user = user_row["username"] st.session_state.user_role = user_row["role"] st.session_state.company_id = user_row["company_id"] st.success(f"✅ تم تسجيل الدخول كمستخدم: {st.session_state.user}") else: st.error("❌ فشل الدخول. تأكد من البيانات أو شركة الدخول.")

تسجيل مستخدم جديد

with st.sidebar.expander("إنشاء مستخدم جديد", expanded=False): su_username = st.text_input("اسم المستخدم الجديد", key="su_username") su_password = st.text_input("كلمة المرور الجديدة", type="password", key="su_password") su_role = st.selectbox("الدور", ["admin","technician"], index=1)

# اختيار الشركة للمستخدم الجديد
su_company = None
all_companies = get_companies()
company_options = [c["name"] for c in all_companies]
if company_options:
    su_company_name = st.selectbox("تابع لشركة", ["-- لا أنتمي --"] + company_options)
    if su_company_name and su_company_name != "-- لا أنتمي --":
        for c in all_companies:
            if c["name"] == su_company_name:
                su_company = c["id"]
                break

if st.button("إنشاء مستخدم"):
    if su_username and su_password:
        existing = find_user(su_username, su_company)
        if existing:
            st.error("اسم المستخدم موجود بالفعل في هذه الشركة.")
        else:
            create_user(su_username, su_password, su_role, su_company)
            st.success("✅ تم إنشاء المستخدم بنجاح.")

st.sidebar.markdown("---")

--------------------------

قبل الدخول - معلومات عامه

--------------------------

if not st.session_state.logged_in: st.info("سجل دخول أو أنشئ مستخدم لبدء إدارة العملاء. يمكنك أيضاً إنشاء شركة جديدة من الشريط الجانبي.") st.stop()

--------------------------

بعد تسجيل الدخول

--------------------------

زر تسجيل الخروج

if st.sidebar.button("تسجيل الخروج"): st.session_state.logged_in = False st.session_state.user = None st.session_state.user_role = None st.session_state.company_id = None st.experimental_rerun()

st.sidebar.write(f"مستخدم: {st.session_state.user}") st.sidebar.write(f"دور: {st.session_state.user_role}") company_info = get_company_by_id(st.session_state.company_id) if st.session_state.company_id else None if company_info: st.sidebar.write(f"شركة: {company_info['name']}")

قائمة التحكم

st.sidebar.subheader("لوحة التحكم") if st.session_state.user_role == "admin": menu = st.sidebar.radio("القائمة", [ "إضافة العميل", "عرض العملاء", "بحث", "تذكير الزيارة", "إضافة فني", "الخريطة", "إحصائيات" ]) else: menu = st.sidebar.radio("القائمة", [ "عرض العملاء", "بحث", "تذكير الزيارة", "الخريطة" ])

--------------------------

وظيفة: إضافة عميل

--------------------------

if menu == "إضافة العميل": st.subheader("➕ إضافة عميل") with st.form("add_form"): name = st.text_input("اسم العميل") phone = st.text_input("رقم التليفون") lat = st.text_input("Latitude (اختياري)") lon = st.text_input("Longitude (اختياري)") notes = st.text_area("ملاحظات") category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"]) last_visit = st.date_input("تاريخ آخر زيارة", datetime.today()) if st.form_submit_button("إضافة"): try: lat_val = float(lat) if lat else None lon_val = float(lon) if lon else None except: lat_val = None lon_val = None comp_id = st.session_state.company_id add_customer(comp_id, name, phone, lat_val, lon_val, notes, category, str(last_visit)) st.success(f"✅ تم إضافة {name} بنجاح.")

--------------------------

وظيفة: عرض العملاء

--------------------------

elif menu == "عرض العملاء": st.subheader("📋 قائمة العملاء") comp_id = st.session_state.company_id customers = get_customers(comp_id) if customers: for c in customers: st.markdown(f"{c['name']} - {c['phone']}") if c['location']: st.markdown(f"🌍 فتح الموقع", unsafe_allow_html=True) if c['phone']: st.markdown(f"💬 واتساب | 📞 اتصال", unsafe_allow_html=True) st.write(f"التصنيف: {c['category']} | آخر زيارة: {c['last_visit']}") st.write("---") else: st.info("لا يوجد عملاء بعد لهذه الشركة.")

--------------------------

وظيفة: بحث

--------------------------

elif menu == "بحث": st.subheader("🔎 البحث عن عميل") keyword = st.text_input("اكتب اسم العميل أو رقم التليفون") if keyword: results = search_customers(st.session_state.company_id, keyword) if results: for c in results: st.markdown(f"{c['name']} - {c['phone']}") if c['location']: st.markdown(f"🌍 فتح الموقع", unsafe_allow_html=True) if c['phone']: st.markdown(f"💬 واتساب | 📞 اتصال", unsafe_allow_html=True) st.write("---") else: st.warning("لا يوجد نتائج.")

--------------------------

وظيفة: تذكير الزيارة

--------------------------

elif menu == "تذكير الزيارة": st.subheader("⏰ العملاء المطلوب زيارتهم (30+ يوم)") today = datetime.today() reminders = [] for c in get_customers(st.session_state.company_id): try: last = datetime.strptime(c['last_visit'], "%Y-%m-%d") if today - last >= timedelta(days=30): reminders.append(c) except: pass if reminders: for c in reminders: st.markdown(f"{c['name']} - {c['phone']}") if c['location']: st.markdown(f"🌍 فتح الموقع", unsafe_allow_html=True) st.write("---") else: st.success("لا يوجد عملاء تحتاج زيارة.")

--------------------------

وظيفة: إضافة فني

--------------------------

elif menu == "إضافة فني": st.subheader("➕ إضافة فني جديد") new_user = st.text_input("اسم المستخدم الجديد") new_pass = st.text_input("كلمة السر الجديدة", type="password") assign_company = None all_companies = get_companies() if all_companies: company_names = [c['name'] for c in all_companies] chosen = st.selectbox("اختر الشركة للفني", company_names, index=0) for c in all_companies: if c['name'] == chosen: assign_company = c['id'] break if st.button("حفظ الفني"): if new_user and new_pass and assign_company: existing = find_user(new_user, assign_company) if existing: st.error("اسم المستخدم موجود بالفعل!") else: create_user(new_user, new_pass, 'technician', assign_company) st.success(f"✅ تم إضافة الفني {new_user} بنجاح!") else: st.error("الرجاء ملء كل الحقول واختيار شركة.")

--------------------------

وظيفة: الخريطة (قمر صناعي) باستخدام pydeck

--------------------------

elif menu == "الخريطة": st.subheader("🗺️ خريطة العملاء (قمر صناعي)") locations = [] for c in get_customers(st.session_state.company_id): try: if c['lat'] is not None and c['lon'] is not None: lat = float(c['lat']) lon = float(c['lon']) locations.append({"name": c['name'], "lat": lat, "lon": lon}) except: pass

if locations:
    df = pd.DataFrame(locations)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lon'].mean(),
            zoom=11,
            pitch=0
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon, lat]',
                get_radius=200,
                pickable=True
            )
        ],
        tooltip={"text": "{name}"}
    ))
else:
    st.info("❌ لا يوجد عملاء لعرضهم على الخريطة.")

--------------------------

وظيفة: إحصائيات بسيطة

--------------------------

elif menu == "إحصائيات": st.subheader("📊 إحصائيات الشركة") customers = get_customers(st.session_state.company_id) total = len(customers) need_visit = 0 categories = {} today = datetime.today() for c in customers: categories[c['category']] = categories.get(c['category'], 0) + 1 try: last = datetime.strptime(c['last_visit'], "%Y-%m-%d") if today - last >= timedelta(days=30): need_visit += 1 except: pass st.write(f"إجمالي العملاء: {total}") st.write(f"عملاء يحتاجون زيارة: {need_visit}") if categories: st.write("توزيع حسب التصنيف:") st.table(pd.DataFrame(list(categories.items()), columns=["تصنيف","عدد"]))

نهاية الملف

ملاحظات:

- هذا تطبيق أساسي يمكن تطويره بإضافة API، رفعه على سيرفر، واستخدام JWT للتوثيق.

- عند التشغيل محلياً: pip install streamlit pydeck

- لتشغيل: streamlit run streamlit_multi_company_app.py
