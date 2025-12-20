import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="Power Life | CRM",
    page_icon="💧",
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

# ================== إنشاء المدير الافتراضي ==================
if not any(u.get("username") == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_json(USERS_FILE, users)

# ================== الجلسة ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ================== صفحة الدخول ==================
def login_page():
    st.title("💧 Power Life")
    st.subheader("تسجيل الدخول")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            user = next((u for u in users if u["username"] == username and u["password"] == password), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.success("تم الدخول")
                st.rerun()
            else:
                st.error("بيانات خاطئة")

# ================== إدارة العملاء (إضافة/تعديل/حذف) ==================
def manage_customers():
    st.subheader("👤 إدارة العملاء")
    
    tab1, tab2 = st.tabs(["➕ إضافة عميل جديد", "⚙️ تعديل / حذف"])
    
    with tab1:
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            location = st.text_input("الإحداثيات (lat,lon)")
            category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            notes = st.text_area("ملاحظات")
            last_visit = st.date_input("تاريخ التركيب/آخر زيارة")
            if st.form_submit_button("حفظ العميل"):
                new_id = max([c['id'] for c in customers], default=0) + 1
                customers.append({
                    "id": new_id, "name": name, "phone": phone, 
                    "location": location, "category": category, 
                    "notes": notes, "last_visit": str(last_visit),
                    "history": [] # سجل الصيانة
                })
                save_json(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ!")

    with tab2:
        if not customers:
            st.info("لا يوجد عملاء للتعديل")
        else:
            cust_to_edit = st.selectbox("اختر العميل", options=customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("الاسم", value=cust_to_edit['name'])
                new_phone = st.text_input("الهاتف", value=cust_to_edit['phone'])
            with col2:
                if st.button("تحديث البيانات"):
                    cust_to_edit.update({"name": new_name, "phone": new_phone})
                    save_json(CUSTOMERS_FILE, customers)
                    st.success("تم التحديث")
                if st.button("❌ حذف العميل"):
                    customers.remove(cust_to_edit)
                    save_json(CUSTOMERS_FILE, customers)
                    st.warning("تم الحذف")
                    st.rerun()

# ================== سجل الصيانة ==================
def service_history():
    st.subheader("🛠️ سجل الصيانة والزيارات")
    if not customers:
        st.info("أضف عملاء أولاً")
        return

    selected_cust = st.selectbox("اختر العميل لتسجيل زيارة", options=customers, format_func=lambda x: x['name'])
    
    with st.expander("📝 تسجيل زيارة جديدة"):
        date = st.date_input("تاريخ الزيارة")
        service_type = st.multiselect("الأعمال التي تمت", ["تغيير شمعة 1", "تغيير شمعة 2", "تغيير شمعة 3", "تغيير ممبرين", "صيانة عامة"])
        cost = st.number_input("التكلفة", min_value=0)
        if st.button("حفظ الزيارة"):
            visit_data = {"date": str(date), "work": service_type, "cost": cost}
            if "history" not in selected_cust: selected_cust["history"] = []
            selected_cust["history"].append(visit_data)
            selected_cust["last_visit"] = str(date) # تحديث آخر زيارة تلقائياً
            save_json(CUSTOMERS_FILE, customers)
            st.success("تم تسجيل الزيارة")

    if selected_cust.get("history"):
        st.write("الزيارات السابقة:")
        st.table(pd.DataFrame(selected_cust["history"]))

# ================== التقارير والبحث ==================
def show_reports():
    st.subheader("📊 التقارير")
    if customers:
        df = pd.DataFrame(customers)
        # ميزة تحميل اكسل
        st.download_button("📥 تحميل قائمة العملاء Excel", 
                           data=df.to_csv(index=False).encode('utf-8-sig'),
                           file_name="customers_power_life.csv", 
                           mime="text/csv")
        st.dataframe(df.drop(columns=["history"], errors='ignore'), use_container_width=True)

# ================== لوحة التحكم الرئيسية ==================
def dashboard():
    user = st.session_state.current_user
    st.sidebar.title(f"مرحباً {user['username']}")
    
    menu = ["التقارير", "البحث", "خريطة العملاء", "سجل الصيانة"]
    if user['role'] == "admin":
        menu.insert(0, "إدارة العملاء")
        menu.append("إضافة فني")
    
    menu.append("تسجيل الخروج")
    choice = st.sidebar.radio("الانتقال إلى", menu)

    if choice == "إدارة العملاء": manage_customers()
    elif choice == "التقارير": show_reports()
    elif choice == "سجل الصيانة": service_history()
    elif choice == "خريطة العملاء":
        from main import show_map # استدعاء دالة الخريطة من الكود الأصلي
        show_map()
    elif choice == "تسجيل الخروج": logout()

# تشغيل التطبيق
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
