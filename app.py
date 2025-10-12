# app.py
import streamlit as st
import sqlite3
import os
from datetime import datetime
from io import BytesIO
import base64

# Optional libs (barcode generation & decoding)
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_LIB = True
except Exception:
    BARCODE_LIB = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    from pyzbar.pyzbar import decode as zbar_decode
    PYZBAR_AVAILABLE = True
except Exception:
    PYZBAR_AVAILABLE = False

# For QR fallback
try:
    import qrcode
    QRCODE_AVAILABLE = True
except Exception:
    QRCODE_AVAILABLE = False

# Map lib (optional)
try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except Exception:
    PYDECK_AVAILABLE = False

# -------------------------
# Config & DB
# -------------------------
DB_PATH = "barolife_stream.db"
BARCODES_DIR = "barcodes"
os.makedirs(BARCODES_DIR, exist_ok=True)

st.set_page_config(page_title="Baro Life Global", layout="wide")
st.markdown("""<style>
    .stApp { background: #ffffff; }
    .container { max-width: 1100px; margin: auto; }
</style>""", unsafe_allow_html=True)

# -------------------------
# DB helpers
# -------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # users
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, fullname TEXT, role TEXT)""")
    # customers
    c.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, address TEXT,
        lat REAL, lon REAL,
        barcode TEXT UNIQUE, created_at TEXT)""")
    # technicians
    c.execute("""CREATE TABLE IF NOT EXISTS technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, created_at TEXT)""")
    # service_logs
    c.execute("""CREATE TABLE IF NOT EXISTS service_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER, technician_id INTEGER,
        barcode TEXT, action TEXT, notes TEXT, created_at TEXT)""")
    # payments
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER, amount REAL, method TEXT, notes TEXT, created_at TEXT)""")
    # events
    c.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT, description TEXT, user TEXT, metadata TEXT, created_at TEXT)""")
    conn.commit()
    # default admin
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username,password,fullname,role) VALUES (?,?,?,?)",
                  ("admin","admin123","مدير النظام","admin"))
    conn.commit()
    conn.close()

def query_df(query, params=()):
    conn = get_conn()
    import pandas as pd
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# -------------------------
# Event logging
# -------------------------
def log_event(event_type, description, user=None, metadata=None):
    created_at = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO events (event_type,description,user,metadata,created_at) VALUES (?,?,?,?,?)",
              (event_type, description, user or "", str(metadata) if metadata else "", created_at))
    conn.commit()
    conn.close()

# -------------------------
# Barcode utilities
# -------------------------
def next_barcode():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM customers ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    next_id = (row[0] + 1) if row else 1
    return f"B-{next_id:05d}"

def generate_barcode_img(code_value):
    """
    Generates barcode PNG in BARCODES_DIR and returns PIL.Image (if possible) or bytes.
    Uses python-barcode (Code128) if available, otherwise QR fallback if qrcode available.
    """
    filename = os.path.join(BARCODES_DIR, f"{code_value}.png")
    if os.path.exists(filename):
        if PIL_AVAILABLE:
            return Image.open(filename)
        else:
            with open(filename, "rb") as f:
                return f.read()

    # Try python-barcode
    if BARCODE_LIB:
        CODE = barcode.get_barcode_class('code128')
        my_code = CODE(code_value, writer=ImageWriter())
        saved_path = my_code.save(os.path.join(BARCODES_DIR, code_value))
        # python-barcode saves as .../code_value.png
        if PIL_AVAILABLE:
            return Image.open(saved_path + (".png" if not saved_path.endswith(".png") else ""))
        else:
            with open(saved_path + (".png" if not saved_path.endswith(".png") else ""), "rb") as f:
                return f.read()
    # Fallback to qrcode
    if QRCODE_AVAILABLE:
        img = qrcode.make(code_value)
        img.save(filename)
        if PIL_AVAILABLE:
            return Image.open(filename)
        else:
            with open(filename, "rb") as f:
                return f.read()

    # Last fallback: create plain text image via PIL if available
    if PIL_AVAILABLE:
        img = Image.new("RGB", (400, 120), color=(255,255,255))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            fnt = None
        draw.text((10,40), code_value, fill=(0,0,0), font=fnt)
        img.save(filename)
        return img

    return None

def pil_image_to_bytes(img):
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio.getvalue()

# -------------------------
# Core CRUD
# -------------------------
def add_customer(name, phone, address, lat, lon, created_by):
    bc = next_barcode()
    created_at = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO customers (name,phone,address,lat,lon,barcode,created_at) VALUES (?,?,?,?,?,?,?)",
              (name, phone, address, lat, lon, bc, created_at))
    conn.commit()
    conn.close()
    # generate barcode file
    generate_barcode_img(bc)
    log_event("add_customer", f"Added customer {name}", user=created_by, metadata={"phone": phone, "barcode": bc})
    return bc

def add_technician(name, phone, created_by):
    created_at = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO technicians (name, phone, created_at) VALUES (?,?,?)", (name, phone, created_at))
    conn.commit()
    conn.close()
    log_event("add_technician", f"Added technician {name}", user=created_by)

def add_service(customer_id, technician_id, barcode_val, action, notes, created_by):
    created_at = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO service_logs (customer_id,technician_id,barcode,action,notes,created_at) VALUES (?,?,?,?,?,?)",
              (customer_id, technician_id, barcode_val, action, notes, created_at))
    conn.commit()
    conn.close()
    log_event("service", f"Service {action} for customer {customer_id}", user=created_by, metadata={"barcode": barcode_val})

def add_payment(customer_id, amount, method, notes, created_by):
    created_at = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments (customer_id,amount,method,notes,created_at) VALUES (?,?,?,?,?)",
              (customer_id, amount, method, notes, created_at))
    conn.commit()
    conn.close()
    log_event("payment", f"Payment {amount} for customer {customer_id}", user=created_by, metadata={"amount": amount})

# -------------------------
# Barcode decode (image)
# -------------------------
def decode_barcode_from_pil(img):
    if not PYZBAR_AVAILABLE:
        return None
    # Ensure RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    decoded = zbar_decode(img)
    if decoded:
        return decoded[0].data.decode("utf-8")
    return None

# -------------------------
# UI
# -------------------------
def authenticate(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,username,fullname,role FROM users WHERE username=? AND password=?", (username,password))
    row = c.fetchone()
    conn.close()
    return row

def main():
    init_db()
    if "user" not in st.session_state:
        st.session_state.user = None
    if "scanned_barcode" not in st.session_state:
        st.session_state.scanned_barcode = ""

    # Sidebar: login & quick actions
    st.sidebar.title("💧 Baro Life - إدارة الصيانة")
    if st.session_state.user:
        st.sidebar.write(f"مرحبًا، {st.session_state.user[2]}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state.user = None
            st.experimental_rerun()
    else:
        st.sidebar.subheader("تسجيل الدخول")
        u = st.sidebar.text_input("اسم المستخدم")
        p = st.sidebar.text_input("كلمة المرور", type="password")
        if st.sidebar.button("دخول"):
            user = authenticate(u, p)
            if user:
                st.session_state.user = user
                log_event("login", f"login {u}", user=u)
                st.experimental_rerun()
            else:
                st.sidebar.error("خطأ في اسم المستخدم/كلمة المرور")

    st.title("💧 Baro Life Global — نظام إدارة الصيانة")
    st.markdown("واجهة متطورة: إنشاء باركود، مسحه بالكاميرا، تسجيل صيانة ودفعات، وسجل الأحداث.")

    # Tabs main
    tabs = st.tabs(["إدارة العملاء", "مسح باركود", "الخريطة", "سجل الأحداث", "إدارة الفنيين"])
    # ---------------- Customers tab ----------------
    with tabs[0]:
        st.header("إضافة عميل جديد")
        with st.form("form_add_customer", clear_on_submit=True):
            name = st.text_input("اسم العميل")
            phone = st.text_input("الهاتف")
            address = st.text_input("العنوان")
            lat = st.text_input("خط العرض (اختياري)")
            lon = st.text_input("خط الطول (اختياري)")
            submit = st.form_submit_button("إضافة وإنشاء باركود")
            if submit:
                try:
                    lat_val = float(lat) if lat else None
                    lon_val = float(lon) if lon else None
                    created_by = st.session_state.user[1] if st.session_state.user else "anon"
                    bc = add_customer(name, phone, address, lat_val, lon_val, created_by)
                    st.success(f"تم إضافة العميل. باركود الفلتر: {bc}")
                    # show barcode image
                    img = generate_barcode_img(bc)
                    if PIL_AVAILABLE and isinstance(img, Image.Image):
                        st.image(img, caption=f"باركود: {bc}")
                    else:
                        st.write(f"ملف الباركود محفوظ: {os.path.join(BARCODES_DIR, bc + '.png')}")
                except Exception as e:
                    st.error("خطأ أثناء الإضافة: " + str(e))

        st.markdown("---")
        st.header("قائمة العملاء")
        df = query_df("SELECT id,name,phone,address,lat,lon,barcode,created_at FROM customers ORDER BY created_at DESC")
        if df.empty:
            st.info("لا يوجد عملاء بعد")
        else:
            st.dataframe(df, use_container_width=True)
            selected_row = st.selectbox("اختر عميل للعمل عليه", options=df["id"].tolist())
            if selected_row:
                cust_row = df[df["id"] == selected_row].iloc[0]
                st.subheader(f"تفاصيل العميل: {cust_row['name']}")
                st.write("هاتف:", cust_row["phone"])
                st.write("عنوان:", cust_row["address"])
                st.write("باركود:", cust_row["barcode"])
                # show barcode image
                img = generate_barcode_img(cust_row["barcode"])
                if PIL_AVAILABLE and isinstance(img, Image.Image):
                    st.image(img, width=240)
                # service logs
                logs = query_df(f"SELECT s.id, s.action, s.notes, s.created_at, t.name as tech FROM service_logs s LEFT JOIN technicians t ON s.technician_id=t.id WHERE s.customer_id={selected_row} ORDER BY s.created_at DESC")
                st.markdown("#### سجل الصيانة")
                if logs.empty:
                    st.info("لا توجد سجلات صيانة")
                else:
                    st.dataframe(logs, use_container_width=True)
                # payments
                pays = query_df(f"SELECT id,amount,method,notes,created_at FROM payments WHERE customer_id={selected_row} ORDER BY created_at DESC")
                st.markdown("#### المدفوعات")
                if pays.empty:
                    st.info("لا توجد مدفوعات")
                else:
                    st.dataframe(pays, use_container_width=True)
                # add service / payment forms
                st.markdown("---")
                st.subheader("تسجيل صيانة")
                with st.form("form_service"):
                    tech_name = st.text_input("اسم الفني (ادخل جديد أو اختر من القائمة)")
                    # existing techs
                    tdf = query_df("SELECT id,name FROM technicians")
                    if not tdf.empty:
                        tech_choice = st.selectbox("اختر فني موجود (اختياري)", options=["---"] + tdf["name"].tolist())
                    else:
                        tech_choice = "---"
                    action = st.selectbox("نوع الإجراء", ["تنظيف", "تغيير فلتر", "فحص", "إصلاح", "آخر"])
                    notes = st.text_area("ملاحظات")
                    sub_srv = st.form_submit_button("تسجيل الصيانة")
                    if sub_srv:
                        try:
                            # ensure technician exists or create
                            final_tech = None
                            tech_to_use = tech_choice if tech_choice != "---" else tech_name
                            if tech_to_use:
                                # find or create
                                row = query_df("SELECT id FROM technicians WHERE name = ?", params=(tech_to_use,))
                                conn = get_conn()
                                c = conn.cursor()
                                c.execute("SELECT id FROM technicians WHERE name=?", (tech_to_use,))
                                r = c.fetchone()
                                if r:
                                    final_tech = r[0]
                                else:
                                    created_at = datetime.now().isoformat()
                                    c.execute("INSERT INTO technicians (name,phone,created_at) VALUES (?,?,?)", (tech_to_use, "", created_at))
                                    conn.commit()
                                    final_tech = c.lastrowid
                                conn.close()
                            add_service(selected_row, final_tech, cust_row["barcode"], action, notes, st.session_state.user[1] if st.session_state.user else "anon")
                            st.success("تم تسجيل الصيانة")
                        except Exception as e:
                            st.error("خطأ في تسجيل الصيانة: " + str(e))
                st.markdown("---")
                st.subheader("تسجيل دفعة")
                with st.form("form_payment"):
                    amount = st.number_input("المبلغ", min_value=0.0, format="%f")
                    method = st.selectbox("طريقة الدفع", ["نقداً", "تحويل بنكي", "محفظة إلكترونية", "أخرى"])
                    pay_notes = st.text_area("ملاحظات عن الدفع")
                    sub_pay = st.form_submit_button("تسجيل الدفع")
                    if sub_pay:
                        try:
                            add_payment(selected_row, float(amount), method, pay_notes, st.session_state.user[1] if st.session_state.user else "anon")
                            st.success("تم تسجيل الدفعة")
                        except Exception as e:
                            st.error("خطأ في تسجيل الدفعة: " + str(e))

    # ---------------- Scan tab ----------------
    with tabs[1]:
        st.header("مسح باركود الفلتر (اختبر على موبايل الفني)")
        st.write("يمكنك: (1) تصوير الباركود بالكاميرا، (2) رفع صورة باركود، أو (3) إدخال رقم الباركود يدوياً.")
        col1, col2 = st.columns([1,1])
        detected_bc = ""
        with col1:
            if PYZBAR_AVAILABLE and PIL_AVAILABLE:
                st.write("التقاط صورة بالكاميرا (Streamlit يدعم كاميرا على الموبايل):")
                img_file = st.camera_input("التقط صورة للباركود")
                if img_file is not None:
                    try:
                        img = Image.open(img_file)
                        decoded = decode_barcode_from_pil(img)
                        if decoded:
                            detected_bc = decoded
                            st.success("تم قراءة الباركود: " + detected_bc)
                        else:
                            st.info("لم يتم قراءة باركود من الصورة. جرب رفع صورة أو إدخال الكود يدوياً.")
                    except Exception as e:
                        st.error("خطأ أثناء معالجة الصورة: " + str(e))
            else:
                st.info("فك الباركود بالكاميرا غير متاح لأن مكتبة pyzbar أو PIL غير مثبتة. يمكنك رفع صورة أو إدخال الكود يدوياً.")

            st.write("أو ارفع صورة باركود:")
            file_up = st.file_uploader("رفع صورة باركود (PNG/JPEG)", type=["png","jpg","jpeg"])
            if file_up is not None:
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(file_up)
                        if PYZBAR_AVAILABLE:
                            decoded = decode_barcode_from_pil(img)
                            if decoded:
                                detected_bc = decoded
                                st.success("تم قراءة الباركود: " + detected_bc)
                            else:
                                st.info("لم يتم قراءة باركود من الصورة.")
                        else:
                            st.info("لا تتوفر مكتبة فك الباركود. استخدم إدخال يدوي أو ثبت pyzbar.")
                    except Exception as e:
                        st.error("خطأ في فتح الصورة: " + str(e))
                else:
                    st.info("Pillow غير مثبتة لقراءة الصورة هنا. قم بتثبيتها لتفعيل هذه الميزة.")

        with col2:
            manual = st.text_input("أدخل رقم الباركود يدوياً")
            if manual:
                detected_bc = manual.strip()

        # If we have barcode detected, show customer
        if detected_bc:
            st.session_state.scanned_barcode = detected_bc
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT id,name,phone,address,lat,lon,barcode,created_at FROM customers WHERE barcode=?", (detected_bc,))
            r = c.fetchone()
            conn.close()
            if r:
                cust = dict(id=r[0], name=r[1], phone=r[2], address=r[3], lat=r[4], lon=r[5], barcode=r[6], created_at=r[7])
                st.success(f"العميل: {cust['name']} — باركود: {cust['barcode']}")
                # show barcode image
                img = generate_barcode_img(cust["barcode"])
                if PIL_AVAILABLE and isinstance(img, Image.Image):
                    st.image(img, width=240)
                # quick actions: register service / payment (short forms)
                st.markdown("### إجراءات سريعة للفني")
                with st.form("quick_service"):
                    tech = st.text_input("اسم الفني", value="")
                    action = st.selectbox("نوع الصيانة", ["تنظيف","تغيير فلتر","فحص","إصلاح","آخر"])
                    notes = st.text_area("ملاحظات")
                    sbtn = st.form_submit_button("تسجيل صيانة الآن")
                    if sbtn:
                        # create technician if needed
                        conn = get_conn()
       
