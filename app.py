# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import pydeck as pdk

# حاول استيراد pyzbar لفك الباركود لو متاح
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    PYZBAR_AVAILABLE = True
except Exception:
    PYZBAR_AVAILABLE = False

DB_PATH = "barolife.db"

# -----------------------
# إعداد الصفحة
# -----------------------
st.set_page_config(page_title="Baro Life Global", layout="wide")
LANG = {
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
    "map": "🗺️ خريطة العملاء",
    "success_login": "✅ تم تسجيل الدخول:",
    "error_login": "❌ اسم المستخدم أو كلمة المرور غير صحيحة",
    "no_customers": "❌ لا يوجد عملاء بعد",
    "view_details": "عرض التفاصيل وسجل الصيانة",
    "add_log": "➕ إضافة سجل صيانة جديد",
    "service_log": "سجل الصيانة السابق",
    "no_log": "لا يوجد سجلات صيانة سابقة لهذا العميل",
    "events": "📝 سجل الأحداث",
    "payments": "سجل المدفوعات",
    "scan_barcode": "مسح باركود الفلتر (أو ارفع صورة)",
    "manual_barcode": "أو أدخل رقم الباركود يدوياً",
    "record_payment": "تسجيل دفعة",
    "amount": "المبلغ",
    "notes": "ملاحظات",
}

# -----------------------
# قاعدة البيانات
# -----------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            fullname TEXT,
            role TEXT
        )
    """)
    # customers
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            lat REAL,
            lon REAL,
            filter_barcode TEXT UNIQUE,
            created_at TEXT
        )
    """)
    # technicians
    c.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            created_at TEXT
        )
    """)
    # service logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS service_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            technician_id INTEGER,
            barcode TEXT,
            action TEXT,
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(technician_id) REFERENCES technicians(id)
        )
    """)
    # payments
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount REAL,
            method TEXT,
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)
    # events (event system)
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            description TEXT,
            user TEXT,
            metadata TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    # انشاء مستخدم افتراضي admin لو مش موجود
    try:
        c.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO users (username, password, fullname, role) VALUES (?, ?, ?, ?)",
                      ("admin", "admin123", "مدير النظام", "admin"))
            conn.commit()
    except Exception:
        pass
    conn.close()

def fetch_df(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# -----------------------
# نظام الأحداث
# -----------------------
def log_event(event_type, description, user=None, metadata=None):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute(
        "INSERT INTO events (event_type, description, user, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
        (event_type, description, user or "", str(metadata) if metadata else "", created_at)
    )
    conn.commit()
    conn.close()

# -----------------------
# وظائف CRUD أساسية
# -----------------------
def add_customer(name, phone, address, lat, lon, barcode, created_by):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("""
        INSERT INTO customers (name, phone, address, lat, lon, filter_barcode, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, address, lat, lon, barcode, created_at))
    conn.commit()
    conn.close()
    log_event("add_customer", f"تم إضافة عميل: {name}", user=created_by, metadata={"phone": phone, "barcode": barcode})

def add_technician(name, phone, created_by):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("INSERT INTO technicians (name, phone, created_at) VALUES (?, ?, ?)", (name, phone, created_at))
    conn.commit()
    conn.close()
    log_event("add_technician", f"تم إضافة فني: {name}", user=created_by, metadata={"phone": phone})

def add_service_log(customer_id, technician_id, barcode, action, notes, created_by):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("""
        INSERT INTO service_logs (customer_id, technician_id, barcode, action, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, technician_id, barcode, action, notes, created_at))
    conn.commit()
    conn.close()
    log_event("service", f"صيانة: {action} للعميل {customer_id} بواسطة الفني {technician_id}", user=created_by,
              metadata={"customer_id": customer_id, "technician_id": technician_id, "barcode": barcode})

def add_payment(customer_id, amount, method, notes, created_by):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("""
        INSERT INTO payments (customer_id, amount, method, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, amount, method, notes, created_at))
    conn.commit()
    conn.close()
    log_event("payment", f"دفعة {amount} على العميل {customer_id}", user=created_by,
              metadata={"customer_id": customer_id, "amount": amount, "method": method})

# -----------------------
# مصادقة (بسيطة جدا)
# -----------------------
def authenticate(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    row = c.fetchone()
    conn.close()
    return row

# -----------------------
# واجهة المستخدم
# -----------------------
def main():
    init_db()
    if "user" not in st.session_state:
        st.session_state.user = None

    # شريط جانبي للإجراءات
    st.sidebar.title(LANG["welcome"])
    if st.session_state.user:
        st.sidebar.write(f"{LANG['success_login']} {st.session_state.user[3]}")
        if st.sidebar.button(LANG["logout"]):
            st.session_state.user = None
            st.experimental_rerun()
    else:
        st.sidebar.subheader(LANG["login"])
        username = st.sidebar.text_input(LANG["username"])
        password = st.sidebar.text_input(LANG["password"], type="password")
        if st.sidebar.button(LANG["submit"]):
            user = authenticate(username, password)
            if user:
                st.session_state.user = user  # row tuple
                log_event("login", f"تسجيل دخول: {username}", user=username)
                st.experimental_rerun()
            else:
                st.sidebar.error(LANG["error_login"])

    # Layout الرئيسي
    st.markdown("## " + LANG["dashboard"])
    cols = st.columns([2, 1])

    with cols[0]:
        # تبويبات رئيسية
        tab = st.tabs(["العملاء", "التقارير و الأحداث", "إدارة الفنيين", "الخريطة"])[0]

    # أبسط تنظيم: نقسم المساحات لعمودين
    left, right = st.columns([2, 1])

    # -----------------------
    # جزء: إضافة عميل و عرض العملاء
    # -----------------------
    with left:
        st.header("📋 إدارة العملاء")
        add_c_exp = st.expander(LANG["add_customer"])
        with add_c_exp:
            with st.form("form_add_customer", clear_on_submit=True):
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
                address = st.text_input("العنوان")
                collat, collon = st.columns(2)
                with collat:
                    lat = st.text_input("خط العرض (اختياري)")
                with collon:
                    lon = st.text_input("خط الطول (اختياري)")
                barcode_input = st.text_input(LANG["manual_barcode"], help="ضع رقم الفلتر أو الباركود")
                submit = st.form_submit_button("حفظ العميل")
                if submit:
                    try:
                        lat_val = float(lat) if lat else None
                        lon_val = float(lon) if lon else None
                        add_customer(name, phone, address, lat_val, lon_val, barcode_input, st.session_state.user[1] if st.session_state.user else "anon")
                        st.success("✅ تم إضافة العميل بنجاح")
                    except Exception as e:
                        st.error("حدث خطأ أثناء إضافة العميل: " + str(e))

        st.markdown("---")
        st.subheader(LANG["show_customers"])
        search = st.text_input(LANG["search"])
        q = "SELECT id,name,phone,address,lat,lon,filter_barcode,created_at FROM customers"
        df_customers = fetch_df(q)
        if search:
            df_customers = df_customers[df_customers["name"].str.contains(search, case=False, na=False) |
                                        df_customers["phone"].str.contains(search, case=False, na=False) |
                                        df_customers["filter_barcode"].str.contains(search, case=False, na=False)]
        if df_customers.empty:
            st.info(LANG["no_customers"])
        else:
            # عرض جدول تفاعلي
            st.dataframe(df_customers, use_container_width=True)
            # تحديد عميل للعمل عليه
            selected = st.selectbox("اختر عميل للعمل عليه (لإضافة سجل صيانة/دفعة)", df_customers["id"].tolist())
            if selected:
                cust = df_customers[df_customers["id"] == selected].iloc[0]
                st.markdown(f"### بيانات العميل: {cust['name']}")
                st.write(f"الهاتف: {cust['phone']}")
                st.write(f"العنوان: {cust['address']}")
                st.write(f"باركود الفلتر: {cust['filter_barcode']}")
                st.write(f"تاريخ الاضافة: {cust['created_at']}")

                # عرض سجل الصيانة الخاص بالعميل
                st.markdown("#### " + LANG["service_log"])
                q_logs = f"""
                    SELECT s.id, s.action, s.notes, s.created_at, t.name as technician
                    FROM service_logs s
                    LEFT JOIN technicians t ON s.technician_id = t.id
                    WHERE s.customer_id = {int(selected)}
                    ORDER BY s.created_at DESC
                """
                df_logs = fetch_df(q_logs)
                if df_logs.empty:
                    st.info(LANG["no_log"])
                else:
                    st.dataframe(df_logs, use_container_width=True)

                # نموذج إضافة سجل صيانة (مع دعم مسح/رفع صورة باركود)
                st.markdown("---")
                st.subheader(LANG["add_log"])
                with st.form("form_add_log", clear_on_submit=True):
                    # قائمة الفنيين
                    techs = fetch_df("SELECT id, name FROM technicians")
                    tech_map = {row["name"]: row["id"] for _, row in techs.iterrows()} if not techs.empty else {}
                    tech_choice = st.selectbox("اختر الفني", options=["---"] + list(tech_map.keys()))
                    action = st.selectbox("نوع الإجراء", ["تنظيف", "تغيير فلتر", "فحص", "إصلاح", "آخر"])
                    notes = st.text_area(LANG["notes"])
                    # محاولة مسح باركود من صورة الكاميرا
                    barcode_detected = ""
                    if PYZBAR_AVAILABLE:
                        st.write(LANG["scan_barcode"])
                        img_file = st.camera_input("التقط صورة للباركود (اختياري)")
                        if img_file is not None:
                            try:
                                img = Image.open(img_file)
                                decoded = decode(img)
                                if decoded:
                                    barcode_detected = decoded[0].data.decode("utf-8")
                                    st.success("تم قراءة الباركود: " + barcode_detected)
                                else:
                                    st.info("لم يتم قراءة أي باركود في الصورة. يمكنك إدخال الرقم يدوياً.")
                            except Exception as ex:
                                st.info("حدث خطأ أثناء محاولة فك الباركود: " + str(ex))
                    else:
                        st.info("مكتبة فك الباركود غير مثبتة. يمكنك إدخال رقم الباركود يدوياً.")

                    manual_bc = st.text_input(LANG["manual_barcode"], value=barcode_detected)
                    add_log_btn = st.form_submit_button("تسجيل الصيانة")
                    if add_log_btn:
                        try:
                            tech_id = tech_map.get(tech_choice) if tech_choice != "---" else None
                            add_service_log(int(selected), tech_id, manual_bc, action, notes, st.session_state.user[1] if st.session_state.user else "anon")
                            st.success("✅ تم تسجيل الصيانة")
                        except Exception as e:
                            st.error("حدث خطأ أثناء تسجيل الصيانة: " + str(e))

                # تسجيل دفعة
                st.markdown("---")
                st.subheader(LANG["payments"])
                with st.form("form_payment", clear_on_submit=True):
                    amount = st.number_input(LANG["amount"], min_value=0.0, format="%f")
                    method = st.selectbox("طريقة الدفع", ["نقداً", "تحويل بنكي", "محفظة إلكترونية", "آخر"])
                    note_pay = st.text_area("ملاحظات عن الدفع")
                    pay_btn = st.form_submit_button(LANG["record_payment"])
                    if pay_btn:
                        try:
                            add_payment(int(selected), float(amount), method, note_pay, st.session_state.user[1] if st.session_state.user else "anon")
                            st.success("✅ تم تسجيل الدفع")
                        except Exception as e:
                            st.error("حدث خطأ أثناء تسجيل الدفع: " + str(e))

    # -----------------------
    # إدارة الفنيين
    # -----------------------
    with right:
        st.header(LANG["add_technician"])
        with st.form("form_add_technician", clear_on_submit=True):
            t_name = st.text_input("اسم الفني")
            t_phone = st.text_input("هاتف الفني")
            add_t_btn = st.form_submit_button("إضافة فني")
            if add_t_btn:
                try:
                    add_technician(t_name, t_phone, st.session_state.user[1] if st.session_state.user else "anon")
                    st.success("✅ تم إضافة الفني")
                except Exception as e:
                    st.error("حدث خطأ: " + str(e))

        st.markdown("---")
        st.subheader("قائمة الفنيين")
        df_techs = fetch_df("SELECT id, name, phone, created_at FROM technicians")
        if df_techs.empty:
            st.info("لا يوجد فنيين بعد")
        else:
            st.dataframe(df_techs, use_container_width=True)

        st.markdown("---")
        # تنبيهات الزيارات القادمة أو المتأخرة (مكان افتراضي: آخر صيانة قبل 30 يوم)
        st.subheader(LANG["reminders"])
        q_last_service = """
            SELECT c.id as customer_id, c.name, c.phone, MAX(s.created_at) as last_service
            FROM customers c
            LEFT JOIN service_logs s ON c.id = s.customer_id
            GROUP BY c.id
        """
        df_last = fetch_df(q_last_service)
        if df_last.empty:
            st.info("لا يوجد بيانات صيانة")
        else:
            # تحويل last_service إلى datetime والتحقق من >30 يوم
            df_last["last_service"] = pd.to_datetime(df_last["last_service"])
            df_last["days_since"] = (pd.Timestamp.now() - df_last["last_service"]).dt.days
            due = df_last[df_last["days_since"].fillna(9999) > 30]
            if due.empty:
                st.write("لا توجد زيارات متأخرة (أكثر من 30 يوم).")
            else:
                st.dataframe(due[["customer_id", "name", "phone", "last_service", "days_since"]], use_container_width=True)

    # -----------------------
    # تبويب: التقارير و سجل الأحداث
    # -----------------------
    st.markdown("---")
    st.header(LANG["events"])
    events_df = fetch_df("SELECT id, event_type, description, user, metadata, created_at FROM events ORDER BY created_at DESC LIMIT 200")
    if events_df.empty:
        st.info("لا يوجد أحداث بعد")
    else:
        st.dataframe(events_df, use_container_width=True)

    # -----------------------
    # خريطة العملاء
    # -----------------------
    st.markdown("---")
    st.header(LANG["map"])
    df_map = fetch_df("SELECT id,name,lat,lon,filter_barcode FROM customers WHERE lat IS NOT NULL AND lon IS NOT NULL")
    if df_map.empty:
        st.info("لا توجد إحداثيات لعرض الخريطة. يرجى إضافة خطوط العرض/طول للعملاء.")
    else:
        # إعداد pydeck
        st.subheader("موقع العملاء على الخريطة")
        # نقاط
        df_map = df_map.dropna(subset=["lat", "lon"])
        df_map["lat"] = df_map["lat"].astype(float)
        df_map["lon"] = df_map["lon"].astype(float)
        initial_view = pdk.ViewState(latitude=df_map["lat"].mean(), longitude=df_map["lon"].mean(), zoom=10, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position='[lon, lat]',
            get_color='[0, 128, 255, 160]',
            get_radius=200,
            pickable=True
        )
        tooltip = {"html": "<b>العميل:</b> {name} <br/> <b>باركود:</b> {filter_barcode}", "style": {"color": "white"}}
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=initial_view, tooltip=tooltip))

    # نهاية الصفحة
    st.markdown("---")
    st.caption("نسخة بسيطة من نظام إدارة الصيانة - Baro Life Global. للتطويرات الإضافية (تنبيهات SMS/WhatsApp, مولد باركود, تسجيل الدخول المتقدم) تواصل معي.")

if __name__ == "__main__":
    main()
