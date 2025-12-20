import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="Power Life | إدارة العملاء",
    page_icon="💧",   # ← قطرة المياه
    layout="wide"
)

# ================== الملفات ==================
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# ================== دوال مساعدة ==================
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== تحميل البيانات ==================
users = load_json(USERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, [])

# ================== إنشاء المدير ==================
if not any(u.get("username") == "Abdallah" for u in users):
    users.append({
        "username": "Abdallah",
        "password": "772001",
        "role": "admin"
    })
    save_json(USERS_FILE, users)

# ================== الجلسة ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ================== تسجيل الخروج ==================
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.experimental_rerun()

# ================== تسجيل الدخول ==================
def login_page():
    st.title("💧 Power Life")
    st.subheader("تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        user = next(
            (u for u in users if u["username"] == username and u["password"] == password),
            None
        )
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success("تم تسجيل الدخول بنجاح")
            st.experimental_rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")

# ================== إضافة عميل ==================
def add_customer():
    st.subheader("➕ إضافة عميل")

    with st.form("add_customer"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
        location = st.text_input("الإحداثيات (lat,lon)")
        category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
        notes = st.text_area("ملاحظات")
        last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())

        if st.form_submit_button("حفظ"):
            customers.append({
                "id": len(customers) + 1,
                "name": name,
                "phone": phone,
                "location": location,
                "category": category,
                "notes": notes,
                "last_visit": str(last_visit)
            })
            save_json(CUSTOMERS_FILE, customers)
            st.success("✅ تم إضافة العميل")

# ================== عرض العملاء ==================
def show_customers():
    st.subheader("📋 قائمة العملاء")
    if customers:
        st.dataframe(pd.DataFrame(customers), use_container_width=True)
    else:
        st.info("لا يوجد عملاء")

# ================== البحث ==================
def search_customer():
    st.subheader("🔍 بحث عن عميل")
    keyword = st.text_input("اكتب الاسم أو رقم الهاتف")

    if keyword:
        results = [
            c for c in customers
            if keyword in c["name"] or keyword in c["phone"]
        ]
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("لا توجد نتائج")

# ================== التذكير ==================
def visit_reminder():
    st.subheader("⏰ عملاء يحتاجون زيارة")
    today = datetime.today()
    due = []

    for c in customers:
        try:
            last = datetime.strptime(c["last_visit"], "%Y-%m-%d")
            if today - last >= timedelta(days=30):
                due.append(c)
        except:
            pass

    if due:
        st.dataframe(pd.DataFrame(due), use_container_width=True)
    else:
        st.success("لا يوجد عملاء متأخرين")

# ================== إضافة فني ==================
def add_technician():
    st.subheader("👷 إضافة فني")

    with st.form("add_tech"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")

        if st.form_submit_button("إضافة"):
            users.append({
                "username": username,
                "password": password,
                "role": "technician"
            })
            save_json(USERS_FILE, users)
            st.success("✅ تم إضافة الفني")

# ================== الخريطة ==================
def show_map():
    st.subheader("🗺️ خريطة العملاء")
    points = []

    for c in customers:
        try:
            lat, lon = map(float, c["location"].split(","))
            points.append({"lat": lat, "lon": lon})
        except:
            pass

    if points:
        st.map(pd.DataFrame(points))
    else:
        st.info("لا توجد إحداثيات صالحة")

# ================== لوحة التحكم ==================
def dashboard():
    user = st.session_state.current_user
    role = user.get("role")

    st.sidebar.title("💧 Power Life")

    menu = [
        "عرض العملاء",
        "بحث",
        "تذكير الزيارة",
        "الخريطة",
        "تسجيل الخروج"
    ]

    if role == "admin":
        menu.insert(0, "إضافة عميل")
        menu.insert(4, "إضافة فني")

    choice = st.sidebar.radio("القائمة", menu)

    if choice == "إضافة عميل":
        add_customer()
    elif choice == "عرض العملاء":
        show_customers()
    elif choice == "بحث":
        search_customer()
    elif choice == "تذكير الزيارة":
        visit_reminder()
    elif choice == "إضافة فني":
        add_technician()
    elif choice == "الخريطة":
        show_map()
    elif choice == "تسجيل الخروج":
        logout()

# ================== تشغيل التطبيق ==================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
