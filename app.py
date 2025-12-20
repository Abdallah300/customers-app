import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="Power Life | CRM",
    page_icon="💧",
    layout="wide"
)

# ================== الملفات ودوال البيانات ==================
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

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

# تحميل البيانات
users = load_json(USERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, [])

# إنشاء المدير الافتراضي إذا لم يكن موجوداً
if not any(u.get("username") == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_json(USERS_FILE, users)

# ================== إدارة الجلسة ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ================== صفحة تسجيل الدخول ==================
def login_page():
    st.title("💧 Power Life")
    st.subheader("تسجيل الدخول")
    col1, _ = st.columns([1, 1])
    with col1:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            user = next((x for x in users if x["username"] == u and x["password"] == p), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("البيانات خاطئة")

# ================== إضافة عميل (تصميم مضغوط) ==================
def add_customer():
    st.subheader("➕ إضافة عميل جديد")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("الاسم")
            phone = st.text_input("الهاتف")
            category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
        with c2:
            location = st.text_input("الإحداثيات (lat,lon)")
            last_visit = st.date_input("آخر زيارة", datetime.today())
            notes = st.text_input("ملاحظات مختصرة") # تم تغييرها من area لـ input لتوفير مساحة
        
        submitted = st.form_submit_button("✅ حفظ بيانات العميل")
        if submitted:
            if name and phone:
                new_id = max([x['id'] for x in customers], default=0) + 1
                customers.append({
                    "id": new_id, "name": name, "phone": phone,
                    "location": location, "category": category,
                    "notes": notes, "last_visit": str(last_visit),
                    "history": []
                })
                save_json(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ بنجاح!")
            else:
                st.error("الاسم والهاتف مطلوبان")

# ================== عرض التقارير والبحث ==================
def show_reports():
    st.subheader("📋 قائمة العملاء")
    if customers:
        df = pd.DataFrame(customers)
        # زر التحميل للاكسل
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل ملف Excel", csv, "customers.csv", "text/csv")
        st.dataframe(df.drop(columns=["history"], errors="ignore"), use_container_width=True)
    else:
        st.info("لا يوجد بيانات")

# ================== سجل الصيانة ==================
def service_history():
    st.subheader("🛠️ سجل الصيانة")
    if not customers: return st.warning("لا يوجد عملاء")
    
    selected = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
    
    with st.expander("📝 تسجيل صيانة جديدة"):
        c1, c2 = st.columns(2)
        with c1:
            work = st.multiselect("العمل", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "صيانة"])
        with c2:
            cost = st.number_input("التكلفة", min_value=0)
        
        if st.button("حفظ الزيارة"):
            visit = {"date": str(datetime.today().date()), "work": work, "cost": cost}
            if "history" not in selected: selected["history"] = []
            selected["history"].append(visit)
            selected["last_visit"] = str(datetime.today().date())
            save_json(CUSTOMERS_FILE, customers)
            st.success("تم التحديث")

# ================== لوحة التحكم ==================
def dashboard():
    user = st.session_state.current_user
    st.sidebar.title(f"Power Life 💧")
    st.sidebar.write(f"مرحباً: {user['username']}")
    
    menu = ["قائمة العملاء", "سجل الصيانة", "بحث"]
    if user['role'] == "admin":
        menu.insert(0, "إضافة عميل")
        menu.append("إضافة فني")
    
    menu.append("تسجيل الخروج")
    choice = st.sidebar.radio("القائمة", menu)

    if choice == "إضافة عميل": add_customer()
    elif choice == "قائمة العملاء": show_reports()
    elif choice == "سجل الصيانة": service_history()
    elif choice == "تسجيل الخروج": logout()
    elif choice == "بحث":
        search = st.text_input("ابحث بالاسم أو الهاتف")
        if search:
            res = [c for c in customers if search in c['name'] or search in c['phone']]
            st.table(res)

# ================== التشغيل ==================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
