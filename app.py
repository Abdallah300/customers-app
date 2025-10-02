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
        "log_saved": "✅ Maintenance Log saved successfully",
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
    # 1. جدول المستخدمين
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 role TEXT)""")
    # 2. جدول العملاء
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
    # 3. جدول سجل الصيانة (الجديد)
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
    
    # تحديث حقل آخر زيارة في جدول العملاء
    c.execute("UPDATE customers SET last_visit=? WHERE id=?", (data["visit_date"], data["customer_id"]))

    conn.commit()
    conn.close()

def get_customer_maintenance_log(customer_id):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM maintenance_log WHERE customer_id=?", conn, params=(customer_id,))
    conn.close()
    return df

# --------------------------
# دالة عرض الخريطة (تم تعديلها لتظهر دائماً)
# --------------------------
def render_customer_map(df, T):
    
    # 1. تحديد بيانات الخريطة الصالحة (التي بها إحداثيات)
    df_map = df.dropna(subset=["lat", "lon"]).copy()

    # 2. تحديد الإحداثيات المركزية الافتراضية
    # إحداثيات افتراضية لمنطقة مركزية (مصر/القاهرة)
    default_lat = 30.0 
    default_lon = 31.2
    default_zoom = 5 

    # 3. تحديد نقطة العرض الأولية
    if not df_map.empty:
        # إذا كان هناك بيانات صالحة، استخدم متوسط الإحداثيات وتكبير محلي
        center_lat = df_map["lat"].mean()
        center_lon = df_map["lon"].mean()
        initial_zoom = 10 
    else:
        # إذا كانت البيانات فارغة، استخدم الإحداثيات الافتراضية وتكبير عام
        center_lat = default_lat
        center_lon = default_lon
        initial_zoom = default_zoom

    # 4. إضافة عمود تلميح جديد
    layers = []
    if not df_map.empty:
        # استخدام .loc لتجنب SettingWithCopyWarning
        df_map.loc[:, 'tooltip_text'] = df_map.apply(lambda row: f"{row['name']} - {row['region']}\nآخر زيارة: {row['last_visit']}", axis=1)
    
        # إعداد طبقة النقاط 
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=df_map,
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 200]',
            get_radius=300,
            pickable=True
        ))
    
    # **ملاحظة:** سيتم عرض الخريطة دائماً باستخدام الإحداثيات الافتراضية إذا كانت layers فارغة.
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11', 
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=initial_zoom,
            pitch=0,
        ),
        layers=layers,
        tooltip={"text": "{tooltip_text}"} if not df_map.empty else None
    ))
    
    # رسائل توضيحية حسب حالة البيانات
    if df.empty:
        st.info("💡 يتم عرض الخريطة الآن على الموقع الافتراضي. لا توجد بيانات عملاء مسجلة.")
    elif df_map.empty and not df.empty:
        st.warning("⚠️ لديك عملاء، لكن لا توجد إحداثيات GPS مسجلة لهم ليتم عرضها كنقاط على الخريطة. يرجى إضافة إحداثيات لعميل واحد على الأقل.")


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
# واجهة تفاصيل العميل وسجل الصيانة
# --------------------------

def show_customer_details(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        st.error("❌ العميل غير موجود")
        st.session_state.view_customer_id = None
        return

    st.header(T["customer_details"])
    
    # عرض التفاصيل الأساسية
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{T['username']}:** {customer['name']}")
        st.markdown(f"**{T['region']}:** {customer['region']}")
        st.markdown(f"**Category / التصنيف:** {customer['category']}")
    with col2:
        st.markdown(f"**{T['phone']}:** {customer['phone']}")
        st.markdown(f"**Last Visit / آخر زيارة:** {customer['last_visit']}")

    st.markdown(f"**Notes / ملاحظات:** {customer['notes']}")
    
    # رابط الملاحة (GPS)
    if customer['lat'] and customer['lon']:
        map_url = f"https://www.google.com/maps/dir/?api=1&destination={customer['lat']},{customer['lon']}"
        st.markdown(f"[{T['open_map']}]({map_url})", unsafe_allow_html=True) 

    st.markdown("---")
    
    # شاشة إضافة سجل صيانة جديد
    st.subheader(T["add_log"])
    with st.form("add_log_form", clear_on_submit=True):
        col_log1, col_log2 = st.columns(2)
        with col_log1:
            tech_name = st.text_input(T["tech_name"], value=st.session_state.user, disabled=True)
            visit_date = st.date_input(T["visit_date"], datetime.today())
            service_type = st.selectbox(T["service_type"], ["تركيب جديد", "صيانة دورية", "تغيير فلاتر", "إصلاح عطل"])
        with col_log2:
            status = st.selectbox(T["status"], ["تم بنجاح", "بحاجة لمتابعة", "تم الإلغاء"])
            next_visit = st.date_input(T["next_visit"], datetime.today() + timedelta(days=90))
            
        report = st.text_area(T["report"], height=100)
        
        if st.form_submit_button(T["save_log"]):
            add_maintenance_log({
                "customer_id": customer_id,
                "technician_name": tech_name,
                "visit_date": str(visit_date),
                "service_type": service_type,
                "status": status,
                "report": report,
                "next_visit_date": str(next_visit)
            })
            st.success(T["log_saved"])
            st.session_state.view_customer_id = customer_id # تحديث الشاشة
            st.session_state.customers_df = get_customers() # تحديث بيانات العملاء (لتحديث آخر زيارة)
            st.rerun()

    st.markdown("---")

    # عرض سجل الصيانة السابق
    st.subheader(T["service_log"])
    log_df = get_customer_maintenance_log(customer_id)
    if not log_df.empty:
        # عرض الأعمدة الرئيسية فقط بترتيب منطقي
        log_df = log_df[["visit_date", "technician_name", "service_type", "status", "report", "next_visit_date"]]
        
        # إعادة تسمية الأعمدة للعرض
        log_df.columns = [
            T["visit_date"],
            T["tech_name"],
            T["service_type"],
            T["status"],
            T["report"],
            T["next_visit"]
        ]
        
        # عرض أحدث سجل أولاً
        st.dataframe(log_df.sort_values(by=T["visit_date"], ascending=False), use_container_width=True)
    else:
        st.info(T["no_log"])

# --------------------------
# واجهة
# --------------------------
st.title(T["welcome"])

# معالجة تسجيل الدخول
if not st.session_state.logged_in:
    if st.button(T["login"]):
        st.session_state.show_login = True

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
            st.session_state.show_login = False
            st.rerun()
        else:
            st.error(T["error_login"])

# بعد تسجيل الدخول
if st.session_state.logged_in:
    if st.sidebar.button(T["logout"]):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.session_state.show_login = False
        st.session_state.view_customer_id = None
        st.success("تم تسجيل الخروج")
        st.rerun()

    st.sidebar.subheader(T["dashboard"])

    menu_options_admin = [T["add_customer"], T["show_customers"], T["search"], T["reminders"], T["add_technician"], T["map"]]
    menu_options_tech = [T["show_customers"], T["search"], T["reminders"], T["map"]]
    
    # تحديد القائمة النشطة
    if st.session_state.user_role == "admin":
        menu = st.sidebar.radio("القائمة الرئيسية", menu_options_admin)
    else:
        menu = st.sidebar.radio("القائمة الرئيسية", menu_options_tech)
    
    # زر العودة من التفاصيل
    if st.session_state.view_customer_id is not None:
        if st.button(T["back_to_list"]):
            st.session_state.view_customer_id = None
            st.rerun()
            
    # عرض صفحة تفاصيل العميل
    if st.session_state.view_customer_id is not None:
        show_customer_details(st.session_state.view_customer_id)
    
    # باقي القوائم
    else:
        # إضافة عميل (مع العرض الفوري للخريطة)
        if menu == T["add_customer"]:
            st.subheader(T["add_customer"])
            with st.form("add_form"):
                name = st.text_input("Name / الاسم")
                phone = st.text_input("Phone / التليفون")
                lat = st.text_input("Latitude (خط العرض)", help="مثال: 30.12345")
                lon = st.text_input("Longitude (خط الطول)", help="مثال: 31.54321")
                region = st.text_input("Region / المنطقة")
                location = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""
                notes = st.text_area("Notes / ملاحظات")
                category = st.selectbox("Category / التصنيف", ["Home / منزل", "Company / شركة", "School / مدرسة"])
                last_visit = st.date_input("Last Visit / آخر زيارة", datetime.today())
                
                if st.form_submit_button("Save / حفظ"):
                    # تأكيد أن الإحداثيات هي أرقام قبل الحفظ
                    try:
                        lat_val = float(lat) if lat else None
                        lon_val = float(lon) if lon else None
                    except ValueError:
                        st.error("❌ تأكد من إدخال Latitude و Longitude كأرقام عشرية صحيحة (بدون فواصل أو أحرف).")
                        st.stop()
                    
                    add_customer({
                        "name": name,
                        "phone": phone,
                        "lat": lat_val,
                        "lon": lon_val,
                        "location": location,
                        "notes": notes,
                        "category": category,
                        "region": region,
                        "last_visit": str(last_visit)
                    })
                    st.success("✅ تم الحفظ")
                    st.session_state.customers_df = get_customers() # تحديث البيانات

                    # **الميزة الجديدة: عرض الخريطة فوراً بعد الحفظ**
                    if lat_val and lon_val:
                        st.subheader(T["map_new_customer"])
                        render_customer_map(st.session_state.customers_df, T)


        # عرض العملاء
        elif menu == T["show_customers"]:
            st.subheader(T["show_customers"])
            df = st.session_state.customers_df
            if not df.empty:
                # عرض كقائمة قابلة للنقر
                for index, row in df.iterrows():
                    col_name, col_region, col_button = st.columns([3, 2, 1])
                    with col_name:
                        st.write(f"**{row['name']}**")
                    with col_region:
                        st.write(row['region'])
                    with col_button:
                        if st.button(T["view_details"], key=f"view_{row['id']}"):
                            st.session_state.view_customer_id = row['id']
                            st.rerun()
            else:
                st.info(T["no_customers"])

        # البحث
        elif menu == T["search"]:
            st.subheader(T["search"])
            keyword = st.text_input("Search / بحث")
            df = st.session_state.customers_df
            if keyword:
                results = df[df.apply(lambda r: keyword.lower() in str(r).lower(), axis=1)]
                if not results.empty:
                    # عرض النتائج كقائمة قابلة للنقر
                    for index, row in results.iterrows():
                        col_name, col_region, col_button = st.columns([3, 2, 1])
                        with col_name:
                            st.write(f"**{row['name']}** - {row['phone']}")
                        with col_region:
                            st.write(row['region'])
                        with col_button:
                            if st.button(T["view_details"], key=f"search_view_{row['id']}"):
                                st.session_state.view_customer_id = row['id']
                                st.rerun()
                else:
                    st.warning("لا يوجد نتائج / No results")

        # التذكير (تم تصحيح الأقواس هنا)
        elif menu == T["reminders"]:
            st.subheader(T["reminders"])
            df = st.session_state.customers_df
            if not df.empty:
                today = datetime.today()
                df["last_visit"] = pd.to_datetime(df["last_visit"], errors="coerce")
                
                # 1. تحديد العملاء الذين لديهم تاريخ زيارة صالح
                valid_visits = df["last_visit"].notna()
                # 2. تحديد العملاء الذين مضى عل
